---
name: motion-long
description: "Fabrique le motion design d'une vidéo longue en 16:9 avec HyperFrames et GSAP, à partir d'un texte ou d'une voix déjà enregistrée : découpage par chapitres, une idée visuelle par scène, chaque mouvement calé sur les mots de la voix, vraies captures d'interface avec curseur, planche à valider, son mixé, passe de critique notée. À utiliser pour « motion design », « vidéo animée en 16:9 », « anime ce script », « tuto en motion », « explainer long format »."
metadata:
  famille: creer
---
# Motion design long format

La voix d'abord. Chaque instant se déduit des mots, donc changer de prise recale tout. Rien ne se rend avant l'accord donné sur la planche.

`SKILL` désigne le dossier de ce fichier. Lis `hyperframes-core` et `gsap` avant d'écrire une scène, s'ils sont installés.

**Outils :** Node 22+, HyperFrames (`npx hyperframes`), ffmpeg, Python 3 avec numpy. Les bruitages viennent du pack de la skill HyperFrames `media-use`.

## 1. Cadrer

Fixe avant tout, en une question au plus :
- **le message :** une phrase, ce que le spectateur saura ensuite ;
- **la marque :** couleurs, polices et logo à mettre dans `marque.css`. Sans charte, annonce que tu gardes le look du gabarit ;
- **la voix :** une voix enregistrée, ou une voix de synthèse (demande l'accord avant de la générer si elle coûte) ;
- **le sujet :** si la vidéo parle d'une interface, regarde la vraie avant d'écrire et reprends ses mots exacts.

## 2. Écrire et découper

Écris le texte mot pour mot, puis découpe-le en chapitres de 2 à 5 minutes. Chaque chapitre est un projet à part : une reprise de voix ne décale que lui.

Suis [le découpage](references/decoupage.md) : pour chaque phrase, décide `ANIMATION`, `MÊME` ou `RIEN`, puis écris chaque scène avec ce qui est dit, ce qui bouge et pourquoi.

Montre ce découpage et attends l'accord avant d'animer.

## 3. Créer le projet et poser la voix

```bash
cp -R SKILL/gabarit <dossier-du-chapitre>
```

Remplace l'exemple de `voix/voix.json` par les vrais mots, et mets le son dans `voix/voix.mp3` ou `voix/voix.wav`. Deux formats de mots sont lus :
- `{"mots": [{"m": "Bonjour", "d": 0.0, "f": 0.4}]}` ;
- la sortie de `npx hyperframes transcribe` (`text`, `start`, `end`).

Avec une transcription, vérifie les mots contre le texte. Si elle se trompe sur un mot clé, prends une autre prise ou corrige le fichier.

## 4. Animer

Écris les scènes dans `scenes.js`, en lisant d'abord [le mouvement](references/mouvement.md). Dans une scène, `t(n)` donne le début du mot n et `f(n)` sa fin. N'écris jamais un temps en dur quand un mot peut le donner. Les captures vont dans `ui/`, avec leur ligne dans `ui/_images.md`.

```bash
python3 SKILL/scripts/construire.py <projet>
npx hyperframes check
```

Ne modifie jamais `index.html` ni `planche.html` : ils sont régénérés.

## 5. Faire valider la planche

`planche.html` montre chaque scène avec ce qui est dit, ce qui bouge et pourquoi. Sers le dossier en local :

```bash
python3 -m http.server 8123 --directory <projet>
```

Rien ne se pose sans accord. Un retour sur une scène se corrige sur cette scène.

## 6. Mixer

Écris les bruitages dans `sons.json`, puis mixe. Le détail est dans [le son](references/son.md).

```bash
python3 SKILL/scripts/mixer.py <projet>
python3 SKILL/scripts/construire.py <projet>
```

La deuxième commande branche `audio/mix.wav` sur la composition.

## 7. Rendre et critiquer

```bash
npx hyperframes render --output renders/chapitre.mp4
```

Passe ensuite [la critique](references/critique.md) : regarde de vraies images, note chaque scène, corrige les 3 pires problèmes. Recommence jusqu'à 8 partout, 3 tours au plus. Consigne les notes dans `critique.md`, avec les mesures. Le son n'est jugé que sur son calage et ses niveaux : dis que tu ne l'as pas écouté.

## 8. Assembler et livrer

Quand tous les chapitres sont validés, liste-les dans `chapitres.txt` (`file '01/renders/chapitre.mp4'`, une ligne par chapitre), puis :

```bash
ffmpeg -f concat -safe 0 -i chapitres.txt -c copy video.mp4
```

Contrôle la durée, le format et le son du fichier final. Montre le rendu, ses notes et ce qui reste à juger à l'oreille.

## Règles qui gardent un rendu juste

- Tout vit dans la timeline GSAP en pause, sans horloge, `Math.random` ni `requestAnimationFrame`. Pour du hasard : `hasard(n)`.
- Pas de `transform` CSS sur un élément que GSAP anime.
- Une vraie capture et un vrai geste valent mieux qu'une interface recréée.
- N'invente aucun fait, chiffre ni résultat.
