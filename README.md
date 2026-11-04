# Skills vidéo

Des skills pour faire de la vidéo avec Claude et HyperFrames.

## Télécharger

[Télécharger le zip](https://codeload.github.com/thomrichard/video-skills/zip/refs/heads/main)

## Les skills

| Skill | Ce qu'elle fait |
|---|---|
| [motion-long](motion-long/SKILL.md) | Le motion design d'une vidéo longue en 16:9, calé sur les mots de la voix, avec planche de validation, son et critique notée |

## Installer

1. Décompresse le zip.
2. Donne ce message à Claude Code, en lui indiquant le dossier décompressé :

```text
Voici une nouvelle skill vidéo : motion-long. Compare-la avec mes skills vidéo actuelles et dis-moi ce qu'elle apporte. Ajoute ce que je valide, sans rien écraser sans me demander. Vérifie aussi que les skills HyperFrames gsap et media-use sont installées.
```

## Il te faut

- Node 22 ou plus, et HyperFrames (`npx hyperframes`)
- ffmpeg
- Python 3 avec numpy
- La skill HyperFrames `media-use`, pour les bruitages

## État

`motion-long` a été testée sur un exemple de 6 secondes. Ses repères pour le 16:9 restent à confirmer sur une vraie vidéo.
