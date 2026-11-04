# La critique

`hyperframes check` trouve les erreurs mécaniques. Cette passe trouve le reste : une scène juste, mais plate ou illisible. On ne montre rien avant.

## Regarder

Regarde avec l'œil d'un directeur artistique sévère, sur de vraies images :

```bash
# Une planche : une image toutes les 5 secondes, 640 px de large
ffmpeg -y -i renders/chapitre.mp4 -vf "fps=1/5,scale=640:-1,tile=4x6" -frames:v 1 renders/planche.jpg
# Une bande de 12 images autour d'un moment clé
ffmpeg -y -ss 12.0 -i renders/chapitre.mp4 -vf "fps=10,scale=320:-1,tile=12x1" -frames:v 1 renders/bande.jpg
```

Si une scène attire l'attention, fais une bande autour de chaque changement. C'est là qu'on attrape les sauts, les chevauchements et les vides.

## Noter

Note chaque scène de 1 à 10 :

| Critère | Ce qu'on regarde |
|---|---|
| Image | À tout moment, l'image est finie et lisible |
| Lisibilité | Tout se lit à 640 px de large |
| Mouvement | Les courbes, le poids, les impacts : rien ne glisse |
| Rythme | L'image suit la voix, sans temps mort ni surcharge |
| Idée | On comprend l'idée sans lire le texte |
| Accord | Ce qu'on voit tombe sur le mot qui le dit |
| Charte | Les couleurs, les polices et la marque sont respectées |
| Son | Chaque son tombe sur son moment, les niveaux sont bons |

## Corriger

1. Écris les 3 pires problèmes, avec le temps exact.
2. Corrige-les, puis rends à nouveau.
3. Recommence jusqu'à 8 partout, 3 tours au plus.

Après 3 tours, montre le rendu en disant ce qui reste sous 8.

## Consigner

`critique.md`, dans le projet :

```markdown
## Tour 2, premier rendu
Problèmes : 1. Scène 3, de 9 à 10 s : écran vide pendant près d'une seconde. 2. …
Corrigé : …

## Tour 3, rendu final
| Scène | Image | Lisibilité | Mouvement | Rythme | Idée | Accord | Charte | Son |

Reste à juger : le niveau de la musique et des bruitages, le ton de la voix.
Mesures : 1920 x 1080, 30 i/s, durée, -14 LUFS, crête, résultat de `hyperframes check`.
```

Mesure le niveau avec :

```bash
ffmpeg -hide_banner -i renders/chapitre.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
```
