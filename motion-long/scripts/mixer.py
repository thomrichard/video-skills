#!/usr/bin/env python3
"""Mixe le son d'un projet motion-long : la voix, une musique qui s'efface sous elle, et les bruitages de sons.json.

    python3 mixer.py <projet> [--musique -20] [--effets 0.55] [--sans-musique]

Écrit audio/mix.wav, exactement de la durée de la voix, à -14 LUFS, et les pistes séparées dans audio/.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import son  # noqa: E402
from mots import lire_mots  # noqa: E402

SR = son.SR
ap = argparse.ArgumentParser()
ap.add_argument("projet")
ap.add_argument("--musique", type=float, default=-20.0, help="niveau de la musique sous la voix, en LU")
ap.add_argument("--effets", type=float, default=0.55, help="volume général des bruitages")
ap.add_argument("--sans-musique", action="store_true")
a = ap.parse_args()

PROJET = Path(a.projet).expanduser().resolve()
AUDIO = PROJET / "audio"
AUDIO.mkdir(exist_ok=True)
mots = lire_mots(PROJET)
TOTAL = mots[-1]["f"] + 0.12
N = int(TOTAL * SR)
source = next((PROJET / f"voix/voix{e}" for e in (".mp3", ".wav", ".m4a") if (PROJET / f"voix/voix{e}").exists()), None)
if source is None:
    raise SystemExit("Aucune voix : mets voix/voix.mp3 ou voix/voix.wav dans le projet.")


def lufs(x):
    p = AUDIO / "_mesure.wav"
    son.ecrire_wav(p, x)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True)
    p.unlink()
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


# ── La voix ──
brut = subprocess.run(["ffmpeg", "-v", "error", "-i", str(source),
                       "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2",
                       "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
voix = np.frombuffer(brut, dtype=np.float32).astype(np.float64).reshape(-1, 2)
voix = np.pad(voix, ((0, max(0, N - len(voix))), (0, 0)))[:N]

# ── La musique, qui baisse quand la voix parle ──
musique = np.zeros((N, 2))
if not a.sans_musique:
    bus = son.Bus(TOTAL + 3)
    pompe = son.groove(bus, TOTAL + 2, 0, 0.6)
    bus.x[: len(pompe)] *= pompe[:, None] ** 0.6
    musique = bus.x[:N].copy()
    pas = int(0.01 * SR)
    rms = np.sqrt(np.mean(voix[: len(voix) // pas * pas].mean(axis=1).reshape(-1, pas) ** 2, axis=1))
    gain, g, cible = np.ones(len(rms)), 1.0, 10 ** (-6 / 20)
    for i, parle in enumerate(rms > 0.02):
        g += ((cible if parle else 1.0) - g) * (0.35 if parle else 0.04)  # descend en 30 ms, remonte en 250 ms
        gain[i] = g
    musique *= np.interp(np.arange(N), np.arange(len(gain)) * pas, gain)[:, None]
    musique *= 10 ** ((lufs(voix) + a.musique - lufs(musique)) / 20)

# ── Les bruitages, ancrés sur les mots ──
effets = son.Bus(TOTAL + 3)
fichier = PROJET / "sons.json"
for e in json.loads(fichier.read_text(encoding="utf-8")) if fichier.exists() else []:
    if e["mot"] >= len(mots):
        raise SystemExit(f"sons.json : le mot {e['mot']} n'existe pas ({len(mots)} mots).")
    ev = {k: v for k, v in e.items() if k not in ("mot", "a", "decalage")}
    ev["t"] = max(0.0, mots[e["mot"]]["d"] + e.get("decalage", 0.0))
    if "a" in e:
        ev["dur"] = max(0.12, mots[e["a"]]["d"] - mots[e["mot"]]["d"])
    son.note_ou_sfx(effets, ev)
bruits = effets.x[:N] * a.effets

# ── Le mélange, à -14 LUFS, plafonné ──
x = voix + musique + bruits
x *= 10 ** ((-14.0 - lufs(x)) / 20)
fond = int(0.015 * SR)
x[-fond:] *= np.linspace(1, 0, fond)[:, None]
son.ecrire_wav(AUDIO / "_brut.wav", np.clip(x, -1, 1))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(AUDIO / "_brut.wav"), "-af", "alimiter=limit=0.84:attack=3:release=40:level=disabled",
                "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(AUDIO / "mix.wav")], check=True)
(AUDIO / "_brut.wav").unlink()
for nom, piste in (("voix", voix), ("musique", musique), ("effets", bruits)):
    son.ecrire_wav(AUDIO / f"piste-{nom}.wav", np.clip(piste, -1, 1))
print(f"mix.wav : {TOTAL:.2f} s · voix {lufs(voix):.1f} LUFS")
