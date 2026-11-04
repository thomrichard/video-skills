"""Lit les mots de la voix d'un projet, dans l'un des deux formats acceptés, et les rend sous une seule forme."""
import json
from pathlib import Path


def lire_mots(projet: Path) -> list:
    """Rend [{"m": mot, "d": début, "f": fin}] depuis voix/voix.json ou voix/transcript.json."""
    for nom in ("voix.json", "transcript.json"):
        chemin = projet / "voix" / nom
        if chemin.exists():
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
            break
    else:
        raise SystemExit(f"Aucun fichier de mots dans {projet / 'voix'} : voix.json ou transcript.json")
    liste = donnees["mots"] if isinstance(donnees, dict) and "mots" in donnees else donnees
    if isinstance(liste, dict):
        liste = liste.get("words", [])
    mots = []
    for x in liste:
        if "m" in x:
            mots.append({"m": x["m"], "d": x["d"], "f": x["f"]})
        else:
            mots.append({"m": x["text"], "d": x["start"], "f": x["end"]})
    if not mots:
        raise SystemExit("Le fichier de mots est vide.")
    return mots
