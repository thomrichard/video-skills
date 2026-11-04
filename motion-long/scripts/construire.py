#!/usr/bin/env python3
"""Fabrique la composition et la planche d'un projet motion-long.

    python3 construire.py <projet>

Lit marque.css, runtime.js, scenes.js et les mots de la voix. Écrit index.html (à rendre) et planche.html (à valider).
Si audio/mix.wav existe, il est branché sur la composition. Sinon, la planche joue la voix si elle existe.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mots import lire_mots  # noqa: E402

GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"

if len(sys.argv) != 2:
    raise SystemExit(__doc__)
projet = Path(sys.argv[1]).expanduser().resolve()
mots = lire_mots(projet)
css = (projet / "marque.css").read_text(encoding="utf-8")
moteur = (projet / "runtime.js").read_text(encoding="utf-8")
scenes = (projet / "scenes.js").read_text(encoding="utf-8")
total = mots[-1]["f"] + 0.12
donnees = "const MOTS = " + json.dumps(mots, ensure_ascii=False, separators=(",", ":")) + ";"

audio = next((f"audio/mix.wav" for _ in [0] if (projet / "audio/mix.wav").exists()), None)
ecoute = audio or next((f"voix/voix{e}" for e in (".mp3", ".wav") if (projet / f"voix/voix{e}").exists()), None)
balise = f'<audio id="son" src="{audio}" data-start="0" data-duration="{total:.3f}" data-track-index="5" data-volume="1"></audio>' if audio else ""

(projet / "index.html").write_text(f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Motion long format</title>
    <script src="{GSAP}"></script>
    <style>
{css}
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; background: var(--fond); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="film" data-start="0" data-width="1920" data-height="1080" data-duration="{total:.3f}">
      {balise}
    </div>
    <script>
{donnees}
{moteur}
{scenes}
(async () => {{
  await document.fonts.ready;
  const film = monterFilm(document.getElementById("root"));
  window.__timelines = window.__timelines || {{}};
  window.__timelines["film"] = film;
}})();
    </script>
  </body>
</html>
""", encoding="utf-8")

(projet / "planche.html").write_text(f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Planche de validation</title>
    <script src="{GSAP}"></script>
    <style>
{css}
      body {{ margin: 0; background: #F4F3EF; color: #1B1D21; font: 16px/1.5 -apple-system, "Segoe UI", Arial, sans-serif; }}
      main {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 64px; }}
      h1 {{ font-size: 24px; margin: 0 0 16px; }}
      #cadre {{ position: relative; width: 100%; aspect-ratio: 16 / 9; overflow: hidden; background: #000; border-radius: 10px; }}
      #film {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}
      .barre-lecture {{ display: flex; align-items: center; gap: 12px; margin: 12px 0 24px; }}
      button {{ font: inherit; cursor: pointer; }}
      #lancer {{ padding: 8px 16px; border: 0; border-radius: 8px; background: #1B1D21; color: #fff; }}
      #position {{ flex: 1; min-width: 0; }}
      #scenes {{ display: grid; gap: 10px; }}
      .scene {{ display: block; width: 100%; text-align: left; padding: 14px 16px; background: #fff; border: 2px solid transparent; border-radius: 10px; color: inherit; }}
      .scene.active {{ border-color: #1B1D21; }}
      .scene b {{ display: block; font-size: 17px; margin-bottom: 4px; }}
      .scene p {{ margin: 4px 0 0; }}
      .scene em {{ font-style: normal; font-weight: 600; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Planche de validation</h1>
      <div id="cadre"><div id="film"></div></div>
      <div class="barre-lecture">
        <button id="lancer">Lancer</button>
        <input id="position" type="range" min="0" max="{total:.3f}" step="0.01" value="0" aria-label="Position dans la vidéo" />
        <span id="compte">0:00</span>
      </div>
      <div id="scenes"></div>
    </main>
    <script>
{donnees}
{moteur}
{scenes}
(async () => {{
  await document.fonts.ready;
  const hote = document.getElementById("film"), cadreFilm = document.getElementById("cadre");
  const ajuster = () => hote.style.transform = `scale(${{cadreFilm.clientWidth / LARGEUR}})`;
  new ResizeObserver(ajuster).observe(cadreFilm); ajuster();
  const film = monterFilm(hote);
  const son = {json.dumps(ecoute)} ? new Audio({json.dumps(ecoute)}) : null;
  const btn = document.getElementById("lancer"), pos = document.getElementById("position"), compte = document.getElementById("compte");
  const liste = document.getElementById("scenes");
  const mmss = s => `${{Math.floor(s / 60)}}:${{String(Math.floor(s % 60)).padStart(2, "0")}}`;
  const marquer = t => {{
    pos.value = t; compte.textContent = mmss(t);
    let idx = 0; SCENES.forEach((s, i) => {{ if (t >= debut(s)) idx = i; }});
    liste.querySelectorAll(".scene").forEach((b, i) => b.classList.toggle("active", i === idx));
  }};
  const aller = t => {{ film.time(t); if (son) son.currentTime = t; marquer(t); }};
  let enCours = false;
  const arreter = () => {{ enCours = false; btn.textContent = "Lancer"; film.pause(); if (son) son.pause(); }};
  const lancer = () => {{ enCours = true; btn.textContent = "Arrêter"; film.play(); if (son) {{ son.currentTime = film.time(); son.play().catch(() => {{}}); }} }};
  btn.addEventListener("click", () => enCours ? arreter() : lancer());
  pos.addEventListener("input", () => aller(parseFloat(pos.value)));
  SCENES.forEach(s => {{
    const b = document.createElement("button"); b.className = "scene";
    const ligne = (titre, texte) => {{ const p = document.createElement("p"); const e = document.createElement("em"); e.textContent = titre + " : "; p.append(e, texte); return p; }};
    const n = document.createElement("b"); n.textContent = `${{mmss(debut(s))}} · ${{s.nom}}`;
    b.append(n, ligne("Dit", s.dit), ligne("Bouge", s.bouge), ligne("Pourquoi", s.pourquoi));
    b.addEventListener("click", () => aller(debut(s)));
    liste.appendChild(b);
  }});
  gsap.ticker.add(() => {{
    if (!enCours) return;
    if (son && !son.paused) film.time(Math.min(son.currentTime, film.duration()));
    if (film.time() >= TOTAL() - .01) {{ arreter(); aller(0); return; }}
    marquer(film.time());
  }});
  marquer(0);
  window.__film = film;
}})();
    </script>
  </body>
</html>
""", encoding="utf-8")
print(f"index.html et planche.html : {len(mots)} mots, {total:.2f} s, son : {audio or 'pas encore de mix'}")
