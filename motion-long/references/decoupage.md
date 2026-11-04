# Le découpage

Il se relit et se corrige avant toute animation. C'est là que se joue la qualité de la vidéo.

## Phrase par phrase

Une ligne par moment de la voix :

| Temps | Ce qui est dit | Décision | Modèle | Ce qui arrive à l'écran |
|---|---|---|---|---|
| 0:12 | « Ce contexte se remplit dès le début » | ANIMATION | Barres empilées | Le titre et le contexte vide |
| 0:15 | « avant ta première question » | MÊME | | « 0 question posée » |
| 0:21 | « les consignes, les outils, les fichiers » | MÊME | | Un bloc par mot |
| 0:30 | « Passons à la suite. » | RIEN | | Le décor reste |

- **ANIMATION :** une nouvelle idée, donc une nouvelle scène.
- **MÊME :** la scène en cours continue et ajoute un élément. C'est le cas le plus fréquent en long format.
- **RIEN :** l'image reste. Une phrase de transition n'a pas besoin d'un effet.

Une règle pour tous les cas : ce qui est déjà prévu se reprend, ce qui ne l'est pas se propose.

## La fiche d'une scène

Chaque scène de `scenes.js` porte ces champs, repris par la planche :

| Champ | Ce qu'il dit |
|---|---|
| `nom` | Le titre court de la scène |
| `de` | Le numéro du mot où elle commence |
| `dit` | La phrase de la voix |
| `bouge` | Ce qu'on voit, dans l'ordre |
| `pourquoi` | Pourquoi cette image aide à comprendre |
| `monte(c)` | L'animation |

## Une bonne idée de scène

- **Elle prouve au lieu d'illustrer.** On doit pouvoir comprendre l'idée sans lire le texte à l'écran.
- **Elle montre le vrai geste.** Pour une interface : la vraie capture, le curseur, le clic, le résultat.
- **Elle compare par le même décor.** Pour opposer deux cas, garde le décor et change un seul élément, comme une page en une heure puis la même page en douze heures.
- **Elle garde un personnage.** Un objet du sujet revient d'une scène à l'autre et relie le chapitre.
- **Elle écrit peu.** Le mot à l'écran reprend le mot de la voix. Elle ne recopie jamais la phrase entière.

## Repères pour le 16:9

Ces repères adaptent au long format une méthode d'abord éprouvée sur un short vertical. Ajuste-les après le premier vrai essai.

- **Image :** 1920 x 1080, 30 i/s, marge de 96 px.
- **Mise en page :** profite de la largeur, avec l'idée d'un côté et sa preuve de l'autre, plutôt qu'une pile centrée.
- **Bas de l'écran :** garde libres les 120 px du bas pour les sous-titres et la barre de lecture.
- **Texte :** 36 px au minimum, 96 px et plus pour le mot clé.
- **Durée d'une scène :** une scène peut durer bien plus longtemps qu'en short, tant que quelque chose change quand la voix avance.
- **Respiration :** laisse des temps calmes. Un film de dix minutes ne peut pas frapper à chaque mot.
- **Ouverture et fin :** ne fais pas boucler la vidéo et ne reprends pas la logique d'affiche à chaque scène. La première image d'un chapitre doit quand même être finie et lisible.
- **Écran de fin :** si la vidéo va sur YouTube, prévois une fin qui laisse la place à ses éléments, et fais-la valider.
