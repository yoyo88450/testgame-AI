# testgame-AI

## Présentation

Ce projet propose deux versions d’un jeu de combat de monstres en Python :
- **Version textuelle** (`game.py`) : jouable dans le terminal, avec des commandes et des choix textuels.
- **Version 2D moderne** (`game_2d.py`) : jouable avec une interface graphique, images, boutons et pop-ups.

---

## Version textuelle (`game.py`)

- Jeu au tour par tour dans le terminal.
- Sélection des attaques, changement de monstre, utilisation d’objets via des menus textuels.
- Progression : combats successifs, expérience, montée de niveau, gestion de l’inventaire.
- Les monstres et ennemis ont des attaques variées, des PV, des niveaux et peuvent évoluer.
- Après chaque victoire, le joueur peut choisir de continuer ou de quitter.
- Idéal pour tester la logique du jeu ou jouer sans interface graphique.

### Lancer la version textuelle
```bash
python game.py
```

---

## Version 2D moderne (`game_2d.py`)

- Interface graphique avec Pygame : images des monstres, boutons, pop-ups, zones de sélection.
- Toutes les fonctionnalités du jeu textuel : combats, inventaire, changement de monstre, progression, expérience, montée de niveau.
- Affichage des monstres avec leurs images (PNG dans le dossier `assets`).
- Zone de sélection des monstres en bas de l’écran : petits ronds pour changer rapidement de monstre.
- Menu fixe en bas pour les actions principales (attaquer, objets, changer).
- Pop-up d’amélioration après chaque victoire, avec boutons cliquables “Oui”/“Non”.
- Gestion des améliorations : PV et attaque augmentés après chaque victoire.
- Interface moderne et intuitive.

### Lancer la version 2D
```bash
python game_2d.py
```

---

## Dossier `assets`

- Contient les images PNG des monstres (générées à partir de SVG).
- Pour ajouter un nouveau monstre, créer un SVG puis le convertir en PNG (voir instructions dans le code).

---

## Dépendances
- Python 3.x
- Pygame (`pip install pygame`)

---

## Auteur
Jeu développé et modernisé avec l’aide de GitHub Copilot.
