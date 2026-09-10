> **Version du 10 septembre :** [montage issu des photos de profil](Photos_2026-09-10/README.md), avec fichiers FreeCAD et positions KiCad synchronisés. Le document ci-dessous décrit une étape antérieure.

# Intégration Touch Bar / PCB V4 — 9 septembre 2026
> Mise à jour à partir des scans : voir [RELEVE_SCANS.md](RELEVE_SCANS.md). La zone active est maintenant 251 × 8,3 mm. Le reste du présent document décrit la première maquette ; les résultats sans collision de cette maquette ne valident pas les nouvelles nappes mesurées.

L'assemblage principal `../assemblage_v4.0.0.FCStd` contient maintenant la zone OLED, les deux nappes pliées, les deux paires de connecteurs et l'enveloppe du RJ45. `Integration_TouchBar_V4.FCStd` est une copie de revue simplifiée (coque transparente), également exportée en STEP. Les objets ajoutés ont le préfixe interne `TBV4_` et des libellés français.

## Sauvegardes avant intervention

- Dépôt mécanique : `f71df3c` (extrusion et esquisses utilisateur).
- Dépôt électronique : `d8c2df4` (ensemble des modifications utilisateur, hors verrous temporaires KiCad).
- Commits locaux ; aucun push effectué.

Les 28 fonctions volumiques d'origine sont conservées, ainsi que leurs placements et les géométries/contraintes de toutes les esquisses. La vérification compare le fichier enregistré au checkpoint.

## Repérage

Le contour provient directement des 40 arêtes (segments et arcs exacts, sans polygonisation) de `Sketch085`, dans `PCB / PCB001`. Il mesure **256 × 18 mm**, épaisseur **1 mm**. Les esquisses originales de placement sont conservées.

| Élément | Centre X local PCB | Centre Y local PCB | Rotation KiCad | Face |
|---|---:|---:|---:|---|
| J1 écran, BM28B0.6-34DS/2-0.35V(53) | 47,525490 | 11,258803 | 0° | F.Cu |
| J2 tactile, AA07-S022VA1-Mockup | 28,363616 | 9,271300 | 90° | F.Cu |
| J4 Ethernet, 634008137521 | 8,826500 | 9,000000 | 270° | F.Cu |

J1/J2 sont centrés dans `Sketch087`/`Sketch086`. Leurs orientations suivent les axes longs des rectangles ; la polarité physique doit être confirmée sur les nappes. J4 ouvre vers l'extrémité X négative, du côté de l'arrivée des nappes.

Conversion : X KiCad = 50 + X local ; Y KiCad = 68 − Y local. Le placement global PCB FreeCAD est (−23,9 ; −3,77 ; −6). La face F.Cu correspond à Z global −5 ; l'écran se trouve côté B.Cu. Cette conversion retourne l'axe Y, pas la face du PCB.

## Chemin des nappes

Les départs passent dans l'ouverture existante de coque à l'extrémité gauche, au-dessus du dos de l'écran. Ils sont repliés entre coque et PCB, passent à l'intérieur du support central, puis se présentent dans l'encoche commune X local 34–37 mm.

- MIPI : deux coudes de 90° de sens opposés, passage dans l'encoche puis arrivée vers J1 à droite.
- Tactile : retour arrondi de **180°**, arrivée vers J2 à gauche, sur la même face F.Cu.
- Les deux connecteurs de nappes sont représentés avec leur embase complémentaire sur le PCB. Leurs enveloppes 3D sont également liées aux empreintes KiCad.

Les zones de transition à plat représentent une découpe de flex provisoire : leur longueur et leur forme ne reproduisent pas un relevé métrologique de la nappe Apple. Le montage réel, l'orientation des contacts et le chemin d'insertion du connecteur complet ne sont pas validés par cette étude de position finale.

## Dimensions encore provisoires

Les références locales identifient la dalle A1706 Samsung AMS983JC01F1A, **2170 × 60 pixels**, mais ne donnent pas de plan mécanique coté complet des nappes ni de la zone active.

- Zone active : 253 × 6,9954 mm, centrée ; hauteur obtenue par le rapport 60/2170 en supposant des pixels carrés. La longueur 253 mm est une hypothèse, pas une cote constructeur.
- Corps d'écran utilisateur inchangé : 262,7 × 10,8 × 1,5 mm.
- Flex : épaisseur 0,12 mm ; largeur de passage MIPI 2,6 mm, tactile 2,4 mm.
- Rayons à la fibre moyenne : MIPI 0,45 mm ; départ tactile 0,40 mm ; retour tactile 1,355 mm.
- Départs de flex et enveloppe de la partie mâle tactile à mesurer. Aucun rayon admissible fabricant n'est revendiqué.
- La hauteur de montage BM28 est 0,6 mm ; la hauteur tactile 0,7 mm et l'enveloppe mâle sont provisoires.

Les paramètres sont regroupés dans `model_display.py` et reportés dans `mechanical_checks.json`. Modifier les propriétés descriptives FreeCAD ne recalcule pas les formes : modifier le script puis le relancer pour régénérer. Les scripts ne changent pas le contour ou les extrusions d'origine.

## Contrôles et problèmes à résoudre

`verification.json` contrôle les solides réellement réouverts après sauvegarde. Avec les enveloppes provisoires, aucune intersection volumique nappe/coque, nappe/PCB, nappe/CIS ou entre nappes n'est détectée. Il s'agit d'un contrôle nominal statique, sans tolérances ni simulation de montage. La zone active se trouve sur la face optique (Z global −9,405 mm).

Le contour KiCad est vérifié indépendamment par réimport du STEP : aire extérieure 4469,141599 mm² contre 4469,141593 mm² dans FreeCAD. Les deux perçages NPTH du RJ45, issus de son empreinte, sont présents dans KiCad et dans son STEP, mais ne sont pas ajoutés à l'extrusion PCB FreeCAD d'origine. Le STEP « board-only » KiCad représente 0,91 mm de diélectrique, hors cuivre/vernis ; l'épaisseur finie déclarée est bien 1 mm.

**RJ45 : l'empreinte V4 déborde du contour de 18 mm par ses plages de blindage.** Elle représente ces plages comme des polygones cuivre sans numéro SH, alors que SH existe au schéma. Le contour est conservé et ce défaut reste visible dans le DRC ; il faut corriger l'empreinte/les fixations et arbitrer localement le contour avant fabrication. L'enveloppe physique 3D utilise le plan Würth et non le rectangle F.Fab de l'ancienne empreinte, dont les dimensions divergent du boîtier constructeur. Les pattes de fixation, contacts et broches de positionnement RJ45 ne sont pas détaillés dans cette enveloppe.

**Tactile :** l'empreinte du dépôt est explicitement `MOCKUP`, à remplacer par le dessin JAE MB-0215 avant routage. Son contact 1 et l'orientation des deux nappes restent à vérifier physiquement. Le schéma et les nets existants ont été repris sans réinterpréter leur brochage.

## Fichiers électroniques

Voir `../../../Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/` : carte KiCad avec J1/J2/J4 seulement, projet associé, modèles STEP, placement détaillé, SVG et DRC. L'ancien `CIS.kicad_pcb`, déjà routé mais antérieur au schéma courant, reste conservé. La nouvelle carte est une base de placement mécanique, sans routage ni implantation des autres composants du schéma.

## Sources

- Workspace : `ReverseAppleTouchBar/schlitzblende/README.md` et `ReverseAppleTouchBar/TouchBar_STM32H7_Integration.html`.
- Schéma courant : `CIS.kicad_sch` du dépôt électronique V4 (cartouche 5.0.0-dev).
- Empreintes : `DISP.pretty/BM28B0.6-34DS_2-0.35V53.kicad_mod`, `DISP.pretty/AA07-S022VA1-Mockup.kicad_mod`, `Library.pretty/CONN_634008137521_WRE.kicad_mod`.
- [Hirose BM28B0.6-34DS/2-0.35V(53)](https://www.hirose.com/product/p/CL0673-5065-0-53).
- [Plan Würth 634008137521, révision 003.001 du 09/07/2025](https://www.we-online.com/components/products/datasheet/634008137521.pdf), page 1 : corps 16,4 × 15,7 mm, hauteur 13,4 mm.

## Régénération

Versions utilisées : FreeCAD 1.0.2 et KiCad 10.0.1 installés dans `/Applications`.

Depuis le workspace, lancer avec le Python FreeCAD `Integration_V4/export_geometry.py`, puis avec le Python KiCad `Integration_Mecanique/build_board.py`, puis avec le Python FreeCAD `model_display.py` et `export_models.py`. `render_review.py` produit les vues PNG. Les scripts FreeCAD avec interface utilisent Cocoa (ne pas imposer `QT_QPA_PLATFORM=offscreen`). `model_display.py` sauvegarde l'assemblage principal : faire un commit avant toute nouvelle itération.

Pour reproduire les vérifications : extraire `git show f71df3c:assemblage_v4.0.0.FCStd` vers `/tmp/sp3ctra-before.FCStd`, exporter le PCB KiCad en STEP `--board-only --user-origin 50x68mm` vers `/tmp/sp3ctra-board.step`, puis exécuter `verify_integration.py` avec le Python FreeCAD. Les vérifications échouent si une géométrie source ou une collision change.
