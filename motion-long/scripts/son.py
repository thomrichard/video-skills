#!/usr/bin/env python3
"""Fabrique la bande son de chaque slide : un groove à 120 BPM + les bruitages calés sur l'image.

    python3 son.py <projet>

Lit carrousel.json -> écrit audio/<slide>.wav (stéréo, 44,1 kHz), exactement de la durée de la slide.
Les traînes qui dépassent la fin sont repliées sur le début : la slide boucle sans clic ni trou.
Dépendances : numpy, ffmpeg (pour décoder les bruitages du pack HyperFrames media-use).

Format d'un son dans carrousel.json -> slides[i].sons :
  {"t": 3.0, "sfx": "impact-bass-1", "gain": 0.9, "pan": 0}   un bruitage du pack
  {"t": 1.0, "note": "A5", "inst": "boop", "gain": 0.6}         une note synthétisée (boop, cloche, pluck)
  {"t": 0.5, "inst": "whoosh", "dur": 0.5, "gain": 0.5}         un souffle synthétisé
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
TEMPS = 0.5
SFX_DIRS = [Path.home() / ".claude/skills/media-use/audio/assets/sfx", Path.home() / ".agents/skills/media-use/audio/assets/sfx"]
NOTES = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
# Progression (ré mineur, chaleureuse) : Rém9 – Si♭maj7 – Fa – Do, une mesure chacun
ACCORDS = [("D", [0, 3, 7, 10, 14]), ("A#", [0, 4, 7, 11]), ("F", [0, 4, 7, 14]), ("C", [0, 4, 7, 9])]


def freq(note: str) -> float:
    nom, octave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((NOTES[nom] + 12 * (octave + 1) - 69) / 12)


def racine(nom: str, octave: int) -> float:
    return freq(f"{nom}{octave}")


def env(n: int, att: float, dec: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(att, 1e-4), 0, 1)
    return a * np.exp(-t / max(dec, 1e-4))


def filtre(x: np.ndarray, bas: float = 0, haut: float = SR / 2) -> np.ndarray:
    """Passe-bande doux dans le domaine fréquentiel (pas de scipy)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if bas > 0:
        m *= 1 / (1 + (bas / np.maximum(f, 1)) ** 4)
    if haut < SR / 2:
        m *= 1 / (1 + (f / haut) ** 4)
    return np.fft.irfft(X * m, len(x))


RNG = np.random.default_rng(7)  # graine fixe : même son à chaque rendu


def bruit(sec: float) -> np.ndarray:
    return RNG.standard_normal(int(sec * SR))


# ── Instruments ────────────────────────────────────────────────
def kick() -> np.ndarray:
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    x[: int(0.004 * SR)] += filtre(bruit(0.004), 1500) * 0.4
    return x * 0.95


def clap() -> np.ndarray:
    x = np.zeros(int(0.3 * SR))
    for k, d in enumerate([0, 0.011, 0.022]):
        b = filtre(bruit(0.25), 900, 3200) * env(int(0.25 * SR), 0.001, 0.012 if k < 2 else 0.09)
        i = int(d * SR)
        x[i : i + len(b)] += b[: len(x) - i]
    return x * 0.35


def hat(ouvert: bool = False) -> np.ndarray:
    d = 0.18 if ouvert else 0.035
    return filtre(bruit(d * 5), 7000) [: int(d * 5 * SR)] * env(int(d * 5 * SR), 0.001, d) * 0.16


def sub(f: float, sec: float) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    e = np.clip(t / 0.008, 0, 1) * np.clip((sec - t) / 0.03, 0, 1)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * e * 0.42


def pad(freqs: list, sec: float) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ph = 2 * np.pi * f * (2 ** (det / 12)) * t
            x += (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.5 + np.sin(ph) * 0.5
    x = filtre(x, 120, 1700)
    e = np.clip(t / 0.25, 0, 1) * np.clip((sec - t) / 0.4 + 0.3, 0, 1) ** 1.5
    return x * e / (len(freqs) * 3) * 0.55


def boop(f: float, dec: float = 0.35) -> np.ndarray:
    n = int(dec * 4 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4.01 * t) * np.exp(-t / 0.05)
    return x * env(n, 0.002, dec) * 0.5


def cloche(f: float) -> np.ndarray:
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in [(1, 1, 0.6), (2.76, 0.45, 0.25), (5.4, 0.25, 0.1)])
    return x * env(n, 0.001, 0.8) * 0.35


def pluck(f: float) -> np.ndarray:
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = (2 * ((f * t) % 1) - 1)
    return filtre(x * np.exp(-t / 0.12), 0, 2600) * 0.3


def whoosh(sec: float) -> np.ndarray:
    n = int(sec * SR)
    t = np.arange(n) / SR
    forme = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2
    return filtre(bruit(sec), 400, 5000) * forme * 0.35


# ── Mixage ─────────────────────────────────────────────────────
class Bus:
    def __init__(self, sec: float):
        self.x = np.zeros((int(sec * SR), 2))

    def add(self, sig: np.ndarray, t: float, gain: float = 1.0, pan: float = 0.0) -> None:
        i = int(round(t * SR))
        if i >= len(self.x) or len(sig) == 0:
            return
        sig = sig[: len(self.x) - i] * gain
        g = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
        self.x[i : i + len(sig)] += sig[:, None] * g[None, :]


_sfx_cache: dict = {}


def sfx(nom: str) -> np.ndarray:
    if nom in _sfx_cache:
        return _sfx_cache[nom]
    for d in SFX_DIRS:
        p = d / f"{nom}.mp3"
        if p.exists():
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
            _sfx_cache[nom] = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
            return _sfx_cache[nom]
    sys.exit(f"Bruitage introuvable : {nom} (pack media-use absent ?)")


def groove(bus: Bus, sec: float, mesure0: int, intensite: float) -> np.ndarray:
    """Batterie + basse + nappe. Renvoie l'enveloppe de pompage (pour baisser la nappe sous le kick)."""
    n_temps = int(round(sec / TEMPS))
    pompe = np.ones(len(bus.x))
    k = kick()
    for b in range(n_temps):
        tb = b * TEMPS
        if b % 2 == 0:  # kick sur 1 et 3
            bus.add(k, tb, 0.9)
            i = int(tb * SR)
            m = min(len(pompe) - i, int(0.3 * SR))
            pompe[i : i + m] = np.minimum(pompe[i : i + m], 1 - 0.55 * np.exp(-np.arange(m) / SR / 0.09))
        else:  # clap sur 2 et 4
            bus.add(clap(), tb, 0.8 * intensite, 0.05)
        for c in range(2):  # charleston en croches
            bus.add(hat(ouvert=(c == 1 and b % 2 == 1)), tb + c * TEMPS / 2, (0.6 + 0.4 * c) * intensite, 0.25)
    for m in range(n_temps // 4):
        nom, inter = ACCORDS[(mesure0 + m) % len(ACCORDS)]
        f0 = racine(nom, 2)
        for c in range(8):  # basse en croches, accent sur les temps
            bus.add(sub(f0 if c % 4 != 3 else f0 * 1.5, TEMPS / 2 * 0.85), m * 2 + c * TEMPS / 2, 0.9 if c % 2 == 0 else 0.6)
        notes = [racine(nom, 3) * 2 ** (i / 12) for i in inter]
        bus.add(pad(notes, 2.3), m * 2, 0.9 * intensite)
    return pompe


def note_ou_sfx(bus: Bus, s: dict) -> None:
    t, g, pan = s["t"], s.get("gain", 0.7), s.get("pan", 0)
    if "sfx" in s:
        bus.add(sfx(s["sfx"]), t, g, pan)
        return
    inst = s.get("inst", "boop")
    if inst == "whoosh":
        bus.add(whoosh(s.get("dur", 0.5)), t, g, pan)
    else:
        f = freq(s.get("note", "A5"))
        sig = {"boop": boop, "cloche": cloche, "pluck": pluck}[inst](f)
        bus.add(sig, t, g, pan)


def fabriquer(slide: dict, mesure0: int, boucle: bool = True) -> np.ndarray:
    """boucle=True : traînes repliées sur le début (slide qui boucle). False : traînes gardées (vidéo continue)."""
    sec = float(slide["duree"])
    n = int(sec * SR)
    musique, effets = Bus(sec + 3), Bus(sec + 3)
    pompe = groove(musique, sec, mesure0, slide.get("intensite", 0.85))
    musique.x[: len(pompe)] *= pompe[:, None] ** 0.6
    for s in slide.get("sons", []):
        note_ou_sfx(effets, s)
    x = musique.x * 0.75 + effets.x
    if not boucle:
        return x
    tete, queue = x[:n].copy(), x[n:]
    tete[: min(n, len(queue))] += queue[: n]  # repli des traînes sur le début
    return tete


def ecrire_wav(path: Path, x: np.ndarray) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def continu(cfg: dict, fin: float) -> np.ndarray:
    """Une seule piste pour toute la vidéo : les slides bout à bout (traînes gardées), puis `fin` secondes
    de groove calme qui s'éteint, à poser sous l'écran de fin."""
    total = sum(float(s["duree"]) for s in cfg["slides"])
    x = np.zeros((int((total + fin + 3) * SR), 2))
    t0, mesure0 = 0.0, 0
    for s in cfg["slides"]:
        y = fabriquer(s, mesure0, boucle=False)
        i = int(round(t0 * SR))
        x[i : i + len(y)] += y[: len(x) - i]
        t0 += float(s["duree"])
        mesure0 += int(round(float(s["duree"]) / 2))
    if fin > 0:
        mesures = int(np.ceil(fin / 2))
        y = fabriquer({"duree": mesures * 2, "intensite": 0.5, "sons": []}, mesure0, boucle=False)
        y[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
        n = int(fin * SR)
        y = y[:n] * np.linspace(0.55, 0.0, n)[:, None] ** 1.3  # plus bas que la musique, s'éteint
        i = int(round(total * SR))
        x[i : i + len(y)] += y
    return x[: int((total + fin) * SR)]


def main_continu() -> None:
    """python3 son.py <projet> --continu [--fin 6.4] -> audio/continu.wav"""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    proj = Path(args[0] if args else ".").expanduser().resolve()
    fin = float(sys.argv[sys.argv.index("--fin") + 1]) if "--fin" in sys.argv else 0.0
    cfg = json.loads((proj / "carrousel.json").read_text())
    x = continu(cfg, fin)
    y = np.tanh(x * 1.2)
    y = y / np.max(np.abs(y)) * 0.89
    (proj / "audio").mkdir(exist_ok=True)
    ecrire_wav(proj / "audio" / "continu.wav", y)
    print(f"audio/continu.wav  {len(y) / SR:.2f} s")


def main() -> None:
    if "--continu" in sys.argv:
        return main_continu()
    proj = Path(sys.argv[1] if len(sys.argv) > 1 else ".").expanduser().resolve()
    cfg = json.loads((proj / "carrousel.json").read_text())
    sortie = proj / "audio"
    sortie.mkdir(exist_ok=True)
    pistes, mesure0 = [], 0
    for s in cfg["slides"]:
        pistes.append((s["nom"], fabriquer(s, mesure0)))
        mesure0 += int(round(s["duree"] / 2))
    # Même gain pour toutes les slides : le volume ne saute pas au swipe
    crete = max(np.max(np.abs(np.tanh(x * 1.2))) for _, x in pistes)
    for nom, x in pistes:
        y = np.tanh(x * 1.2) / crete * 0.89  # douce saturation, crête à -1 dBFS
        ecrire_wav(sortie / f"{nom}.wav", y)
        print(f"audio/{nom}.wav  {len(y) / SR:.2f} s")


if __name__ == "__main__":
    main()
