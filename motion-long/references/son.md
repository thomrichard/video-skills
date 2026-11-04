# Le son

`mixer.py` assemble trois pistes : la voix, une musique qui s'efface sous la voix, et les bruitages calés sur les mots. La musique et les bruitages sont fabriqués en local, sans IA et sans coût.

```bash
python3 SKILL/scripts/mixer.py <projet> --musique -20 --effets 0.55
```

Il écrit `audio/mix.wav`, exactement de la durée de la voix, et les pistes séparées `audio/piste-*.wav`.

## `sons.json`

Une ligne par événement, ancrée sur un mot. `decalage` ajoute des secondes, en plus ou en moins.

```json
[
  {"mot": 3, "sfx": "click", "gain": 0.7},
  {"mot": 3, "sfx": "impact-bass-1", "gain": 0.45, "decalage": 0.02},
  {"mot": 5, "note": "A4", "inst": "boop", "gain": 0.35},
  {"mot": 6, "a": 9, "inst": "whoosh", "gain": 0.28}
]
```

- **`sfx` :** `click`, `click-soft`, `pop`, `ping`, `chime`, `sparkle`, `impact-bass-1`, `impact-bass-2`, `whoosh-cinematic`. Vérifie le pack `media-use` pour la liste complète.
- **`note` et `inst` :** `boop`, `pluck` ou `cloche`, avec une note comme `D5`. Une suite montante accompagne bien une liste qui se remplit.
- **`whoosh` :** dure du mot `mot` au mot `a`, ou `dur` secondes.

## Réglages de départ

Ils viennent du short de référence, et restent à confirmer à l'oreille :

| Réglage | Valeur |
|---|---|
| Niveau final | -14 LUFS, crête limitée vers -1,5 dB |
| Musique sous la voix | -20 LU |
| Effacement sous la voix | -6 dB, descente en 30 ms, remontée en 250 ms |
| Volume général des bruitages | 0,55 |
| Voix | Coupe-bas à 70 Hz, compression légère |

## En long format

- **Peu de bruitages :** réserve-les aux moments qui changent quelque chose. Partout, ils fatiguent vite.
- **Chaque son a son image :** s'il ne tombe sur rien, retire-le.
- **Musique :** si elle lasse sur la durée, baisse-la, ou retire-la avec `--sans-musique`.
- **Limite :** on juge ici le calage et les niveaux. Seule une oreille humaine peut valider le rendu.
