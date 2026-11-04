# Le mouvement

## Trois règles

1. **Une entrée a une direction et un poids.** L'opacité seule ne sert qu'aux sorties discrètes.
2. **Rien ne glisse.** Un déplacement accélère, ralentit, puis se pose.
3. **Le mouvement tombe sur le mot.** Il part du mot qui le justifie, avec `t(n)`.

## Ce que `c` donne à une scène

| Nom | Rôle |
|---|---|
| `c.tl` | La timeline de la scène |
| `c.t(n)`, `c.f(n)` | Le début et la fin du mot n, en temps de scène |
| `c.dur` | La durée de la scène |
| `c.m` | Le calque où poser les éléments |
| `c.q(s)`, `c.qa(s)` | Chercher dans la scène |

## Les aides de `runtime.js`

| Aide | Effet | Pour |
|---|---|---|
| `nouv(parent, classe, style, html)` | Crée un élément | Tout |
| `pop(tl, el, t)` | Apparaît avec un rebond | Une étiquette, une pastille |
| `frappe(tl, el, t)` | Arrive de plus grand et se pose | Le mot clé |
| `glisse(tl, el, t, {x})` | Entre sur le côté | Un panneau, une colonne |
| `impact(tl, el, t)` | S'écrase puis rebondit | Un choc sur un élément |
| `secoue(c, t)` | Secoue toute la scène | Un moment fort, rarement |
| `anneau(c, x, y, t)` | Onde qui s'élargit | Le point d'un clic |
| `monterCurseur(c, x, y)` | Pose le curseur | Une interface |
| `vers(c, cur, x, y, t, d)` | Déplace le curseur | Une interface |
| `clic(c, cur, x, y, t)` | Enfonce le curseur, onde au point | Une interface |
| `cadre(c, x, y, l, h)` | Cadre de sélection | Désigner une zone |
| `barre(c, el, t)` | Barre un élément | Contredire une idée |
| `hasard(n)` | Nombre fixe entre 0 et 1 | Tout hasard |

Crée d'autres aides si la scène le demande, puis garde celles qui reviennent.

## Styles à éviter

- Un titre seul au milieu d'un fond vide.
- Tout qui entre en fondu.
- Un mouvement linéaire, ou qui s'arrête net.
- Des décorations sans rôle : étiquettes dans les coins, cadres, filets.
- Des lueurs, des dégradés ou des ombres sur des éléments d'interface.
- Des explosions de particules génériques.
- Du texte qui se chevauche pendant un changement : le nouveau entre après la sortie de l'ancien.
- Du texte flou, agrandi au-delà de sa taille de départ.
- Une scène qui reste vide pendant que la voix avance : garde l'élément précédent jusqu'à ce que le suivant arrive.
- Le curseur posé sur le mot à lire.

## Pièges techniques

- Ajoute `immediateRender: false` à un `fromTo` qui ne doit pas s'appliquer avant son départ. Les aides le font déjà.
- Pour un élément caché au départ, pose `autoAlpha: 0` avec `gsap.set`.
- Tout ce qui sort de l'écran doit le faire exprès : marque-le `data-layout-allow-overflow`.
