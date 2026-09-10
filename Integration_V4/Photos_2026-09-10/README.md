# Montage écran — photos de profil du 10 septembre 2026

Le cheminement nominal est maintenant continu, sans intersection entre les deux nappes ni avec les pièces actives contrôlées. Les longueurs développées et les contours relevés dans les scans sont conservés. Ce résultat est une **variante de montage à valider sur la pièce**, avec des adaptations du PCB ; il ne constitue pas une implantation qualifiée pour fabrication.

## Fichiers à ouvrir

- [Assemblage complet FreeCAD](assemblage_v4.0.0_montage_ecran.FCStd) : copie de l'assemblage courant, avec les nouvelles nappes, connecteurs et PCB. Le corps `PCB_Photos` contient une esquisse de contour et une extrusion de 1 mm éditables. Les deux nouvelles esquisses `J1_Implantation_Photos` et `J2_Implantation_Photos` portent les positions nominales.
- [Revue légère FreeCAD](TouchBar_Montage_Photos.FCStd) et [STEP de revue](TouchBar_Montage_Photos.step).
- Projet électronique : `CIS/Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/Montage_Photos/CIS_Montage_Photos.kicad_pro`.
- [Vue des nappes](detail_nappes.png), [profil des plis](profil_plis.png), [vue de dessus](implantation_nappes.png).

L'assemblage source `assemblage_v4.0.0.FCStd` est conservé au checkpoint **323c74e**, qui inclut les travaux WHEC présents au début de cette intervention. La variante complète reprend cet état. Les résultats de la précédente `Proposition_Scans` concernent un ancien cheminement et ne décrivent pas cette variante.

## Données et hypothèses

Données utilisateur : zone active **251 × 8,3 mm**, retraits 10,5 / 1,2 / 1,5 / 1 mm ; flex **0,150 mm** ; épaisseurs maximales flex compris **1,15 mm Touch** et **1,50 mm Display**. Les quatre PDF originaux et les contours relevés sont archivés dans `../scans_2026-09-09/`.

La confirmation et les quatre photos de profil reçues le 10 septembre établissent le départ horizontal sous l'écran et la possibilité d'amorcer le pli près du bord. Les photos reçues dans la conversation n'ont pas été converties en nouvelles cotes métriques.

- Les deux départs sont tangents à l'horizontale au dos de l'écran, à Z global −7,825 mm (flex tangent au dos à −7,9 mm). Le point de départ longitudinal reste à X 2 mm pour Touch et 3 mm pour Display.
- Le premier pli Touch commence à X 0,3 mm, après 1,7 mm horizontal ; Display commence à X 3 mm, avec une tangente horizontale.
- Les plis utilisent deux quarts de cercle de **rayon neutre 0,2 mm**, séparés par une partie droite. Le rayon intérieur est donc 0,125 mm. **Ce rayon est une hypothèse de montage serré, pas une limite garantie par le fabricant ni une mesure extraite des photos.**
- Display passe sous Touch, puis remonte à droite dans l'encoche. Touch remonte à gauche et se retourne de 180° ; les deux embases se trouvent sur F.Cu.
- Le recalage transversal de Display vaut **−0,25 mm** par rapport au relevé précédent. C'est un ajustement de position dans l'incertitude du scan, à mesurer sur la pièce. Aucun contour n'a été rétréci et aucune longueur allongée pour obtenir le passage.
- Les zones larges comportant l'électronique restent des **enveloppes conservatrices** à l'épaisseur maximale fournie. Les surfaces métalliques visibles sont distinguées, mais l'épaisseur détaillée des portions noires n'a pas été mesurée. La hauteur proposée dépend de cette enveloppe.
- Les têtes terminales restent planes. La fin du pli Display précède sa zone rigide relevée de seulement 0,3 mm : marge inférieure à l'incertitude du relevé.

## Implantation nominale synchronisée

Repère local PCB d'origine, en mm ; KiCad utilise X = 50 + X local, Y = 68 − Y local. Les décimales décrivent le calcul, pas une précision métrologique.

| Fonction | Référence | X local PCB | Y local PCB | Rotation KiCad | Face |
|---|---|---:|---:|---:|---|
| Display | J1, BM28B0.6-34DS | 41,293363 | 11,320000 | 0° | F.Cu |
| Touch | J2, AA07-S022VA1 Mockup | 25,150637 | 9,475500 | 270° | F.Cu |
| Ethernet | J4, Würth 634008137521 | 8,826500 | 9,000000 | 270° | F.Cu |

Les empreintes sont verrouillées. Les affectations électriques de leurs 76 plages renseignées sont reprises de la netlist du schéma V4. Le repère de broche 1 sérigraphié de J1 a été déplacé de 0,8 mm vers l'intérieur du PCB dans une copie locale de l'empreinte, sans modifier ses pads. L'identification physique de la broche 1 sur les nappes reste à confirmer avec le connecteur réel.

## Adaptations contenues dans cette variante

1. **PCB relevé de 1,6 mm** : face inférieure à Z global −4,4 mm au lieu de −6 mm. Le PCB conserve son épaisseur de 1 mm. Cette hauteur laisse passer les enveloppes empilées ; les fixations de carte ne sont pas redessinées ici.
2. Encoche commune toujours large de **3 mm**, recentrée à X **35 mm**, fond à Y **7,8 mm**. Les rayons de 1 mm du contour source sont conservés. Le reste du contour extérieur est repris des arcs et segments FreeCAD.
3. **Fenêtre de dégagement sous le connecteur CIS existant** : X 224,365 à 241,815 mm ; Y 1,585 à 7,785 mm ; angles R 0,5 mm. Sans cette fenêtre, le PCB relevé intersecte le connecteur CIS sur 24,151 mm³. Le jeu nominal minimum obtenu est 0,288 mm.
4. Les deux perçages de positionnement RJ45 Ø3,2 mm issus de l'empreinte KiCad sont également représentés dans le PCB FreeCAD.

Ces adaptations sont présentes dans les fichiers de variante ci-dessus. Elles doivent être examinées avec la fixation du PCB, le raccordement CIS et son éventuel remplacement par les travaux WHEC en cours.

## Vérifications et limites

Les rapports [fold_plan.json](fold_plan.json), [mechanical_checks.json](mechanical_checks.json) et [verification.json](verification.json) contiennent les mesures reproductibles.

- Chaque flex est un solide valide et continu. Écart de volume plié/déplié : Touch inférieur à 10⁻¹² ; Display **0,00952 %**, dû à l'approximation de la racine courbe et légèrement conique.
- Aucune intersection nominale entre les deux nappes ; jeu minimal entre flex Touch et enveloppe Display : **0,150 mm**.
- Aucune intersection avec coque, écran, PCB adapté, CIS et les pièces actives contrôlées. Jeux flex/coque minimums : **0,0875 mm Touch**, **0,0587 mm Display**. Ces jeux sont **inférieurs aux incertitudes de relevé** ; ils ne garantissent pas un montage réel sans contrainte.
- Le contrôle élargi examine 42 solides source. Les références masquées `TC2030_IDC` (outil de programmation) et ancien modèle Ethernet présentent des intersections si on les réactive ; elles sont consignées séparément dans le rapport, et leur compatibilité n'est pas revendiquée.
- Contour complet KiCad/FreeCAD, fenêtre CIS et perçages compris : différence surfacique d'environ **8 × 10⁻⁶ mm²**. Contrôle indépendant par réimport STEP KiCad.
- L'écran, les nappes et les trois connecteurs sont présents dans l'export 3D KiCad et leur placement a été comparé au modèle FreeCAD. Le STEP KiCad exporte ici un diélectrique de 0,91 mm et un plan d'appui des modèles à 0,995 mm ; le PCB fini déclaré reste à 1 mm.
- **Aucune violation DRC de placement J1/J2.** Restent **4 erreurs et 2 avertissements sur J4**, déjà présents dans son empreinte V4 : blindages au-delà du contour, proximité des trous et sérigraphie. Carte non routée : 34 éléments non connectés.
- **J2 reste une empreinte de maquette**, explicitement signalée dans la bibliothèque V4. Le plan JAE MB-0215 ou un relevé dimensionnel fiable est nécessaire pour figer son empreinte et l'accouplement. Les hauteurs des petites embases et des plugs sont des enveloppes provisoires.
- Le calcul vérifie la position montée ; il ne simule pas toute la trajectoire d'insertion des connecteurs, les efforts, les tolérances, la tenue électrique des plis ou le rayon admissible du flex.

## Régénération

Dans le dépôt mécanique, avec le Python embarqué de FreeCAD :

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/python Integration_V4/fold_photos.py
/Applications/FreeCAD.app/Contents/Resources/bin/python Integration_V4/build_photos_geometry.py
/Applications/FreeCAD.app/Contents/Resources/bin/python Integration_V4/render_photos.py
```

Les paramètres de pli se trouvent dans `../fold_photos.py`, dictionnaire `PARAMS`. Le rendu nécessite une session graphique macOS. Le contour est régénéré depuis le fichier source d'assemblage présent au moment de l'exécution. Après une évolution du CIS ou de la coque, relancer tous les contrôles.

Le README du projet KiCad décrit sa génération et les exports. Exécuter les commandes KiCad successivement, car elles peuvent prendre un verrou sur le fichier projet. Après l'export board-only vers `/tmp/photos_board.step` et l'export complet STEP dans le dossier KiCad, lancer `../verify_photos.py` avec le Python FreeCAD.
