> **Version du 10 septembre :** [montage issu des photos de profil](Photos_2026-09-10/README.md), avec fichiers FreeCAD et positions KiCad synchronisés. Le document ci-dessous décrit une étape antérieure.

# Reprise à partir des scans — état non validé du montage

## Réalisé

Les quatre PDF utilisateur sont archivés dans `scans_2026-09-09/`, avec les cotes textuelles, avant modification du modèle (commit `ccf3203`). Leurs images JPEG natives sont à 200 dpi : 0,127 mm/pixel. La périodicité mesurée du quadrillage est comprise entre 7,87 et 7,89 pixels/mm, cohérente avec cette échelle. Aucun texte du PDF n'a été traité comme une instruction.

L'assemblage principal a reçu **uniquement la correction de la zone active** : 251 × 8,3 mm ; retraits gauche 10,5, droit 1,2, haut 1,5, bas 1 mm, connecteurs à gauche en vue de face. L'extrusion d'écran d'origine est conservée. Les anciennes nappes de l'assemblage principal restent des témoins provisoires ; le nouveau relevé et son étude de pliage sont dans **TouchBar_Scans_Proposition.FCStd**, pas adoptés dans l'assemblage.

Les contours des deux nappes sont relevés avec leurs épaulements, leurs zones larges, leurs queues étroites et leurs têtes décalées. Leurs deux états, déplié et plié, sont présents dans le fichier de revue. Les images `Touch_releve.png` et `Display_releve.png` superposent les contours aux pixels sources ; le centre de chaque connecteur est marqué par une croix.

L'épaisseur de flex est **0,150 mm**. Les enveloppes des îlots portant les blindages ont une épaisseur totale, flex compris, de **1,15 mm pour Touch** et **1,50 mm pour Display**. Les petites parties mâles aux extrémités sont distinctes de ces blindages. La hauteur uniforme donnée aux îlots noirs est une enveloppe conservative : le scan ne permet pas de relever leurs variations de hauteur. Les parties métalliques visibles ont un repérage de surface séparé.

## Fidélité et limites du relevé

`measured_geometry.json` sépare cotes utilisateur, pixels relevés, géométrie dérivée et hypothèses. Le front du tactile est 642 (contrôle verso 643) ; le front du display est 645 (contrôle verso/connecteur 644). L'autre nappe repliée est exclue du contour relevé.

Les contours sont relevés manuellement. À cette résolution, avec la nappe non parfaitement plane, on retient une estimation de ±0,25 mm sur les bords et **±0,5 mm sur les centres**, sans prétendre à une certification métrologique. Les offsets 2/3 mm sont pour l'instant interprétés comme des retraits depuis le petit bord, vers l'intérieur : cette interprétation attend confirmation.

La coordonnée développée `u` est mesurée depuis le départ de la nappe ; `v` depuis le bord long supérieur, écran vu de face connecteurs à gauche. Centres nominaux :

| Nappe | u, mm | v, mm | Orientation du grand axe |
|---|---:|---:|---|
| Touch | 50,006 | 5,9055 | Transversal à la nappe |
| Display | 43,450 | 8,0000 | Longitudinal à la nappe |

Le générateur conserve la longueur de la fibre moyenne. L'erreur numérique de volume du flex plié par rapport à l'aire dépliée × 0,150 mm est inférieure à 0,01 %. Les transitions courbes à largeur variable sont discrétisées à 0,08 mm maximum ; les arcs de largeur constante sont circulaires exacts. Les zones rigides et les têtes sont tenues hors des plis. Cette conservation géométrique ne valide pas les rayons admissibles du flex Apple.

Les positions en Z des départs (-7,825 / -8,075 mm), les plans de rangement des îlots, les rayons et les hauteurs des petits connecteurs sont encore des hypothèses de montage. En particulier la hauteur de l'embase tactile de la bibliothèque est issue d'une empreinte MOCKUP. Les scans ne déterminent pas non plus le numéro 1 de chaque connecteur de façon fiable.

## Étude de placement : interférences encore présentes

Le modèle teste une superposition des îlots : tactile bas, display au-dessus, avec le PCB relevé de **1,6 mm** (Z bas proposé -4,4 au lieu de -6 mm). Les positions calculées pour cette hypothèse sont reprises exactement dans un **PCB KiCad séparé**, `Integration_Mecanique/Proposition_Scans/CIS_Proposition_Scans.kicad_pcb`.

| Connecteur | X local PCB, mm | Y local PCB, mm | Rotation KiCad |
|---|---:|---:|---:|
| J1 Display | 37,0876 | 11,5700 | 0° |
| J2 Touch | 18,4621 | 9,4755 | 270° |

Ces valeurs numériques ne constituent pas une précision physique supérieure à celle du relevé. La conversion reste X KiCad = 50 + X local, Y KiCad = 68 − Y local. Le grand axe et le sens géométrique sont reportés ; l'orientation électrique doit être vérifiée sur les contacts.

L'encoche testée est centrée à X = 30,5576 mm, de largeur 4,8 mm, fond à Y = 8 mm, rayons 1 mm. **Ce n'est pas une solution de montage validée.** La surélévation seule ne résout pas :

- l'intersection des nappes entre elles près de leur traversée commune ;
- l'interférence de leurs parties larges avec le support intérieur de coque, autour de X local 19,8–25 mm / Y > 13,5 mm ;
- la proximité de J2 avec les plages de soudure du RJ45, qui provoque des collisions de cuivre dans KiCad.

`proposal_checks.json` donne les volumes exacts d'interférence avec la coque et les deux positions de PCB. Les solides rouges du fichier FreeCAD montrent les interférences entre nappes et avec la coque. Le DRC du PCB séparé contient 47 violations, dont des courts-circuits par chevauchement J2/J4 : **ne pas router ni fabriquer cette variante**. Le PCB d'intégration précédent reste intact.

Il faut décider du rangement latéral/vertical des nappes et des modifications acceptables du PCB/support intérieur, puis refaire l'implantation. Les cotes de scan seules ne permettent pas de déclarer les connecteurs « parfaitement placés » dans la mécanique actuelle. Les questions sur l'axe des offsets 2/3 mm et la liberté d'adapter la hauteur/encoche sont en attente de réponse.

## Scripts

- `measure_scans.py` : relevé traçable et superpositions sur scans ;
- `fold_measured.py` : état déplié et hypothèse de pliage, contrôles de volume ;
- `build_proposal_geometry.py` : variante de contour et tests contre la mécanique existante ;
- `render_measured_review.py` : revue couleur, interférences et STEP ;
- `update_optical_area.py` : applique les seules cotes optiques confirmées au fichier principal ;
- `model_display.py` : générateur historique des nappes simplifiées, **ne pas utiliser pour remplacer le modèle issu des scans**.

Les scripts de génération du pliage/proposition produisent des fichiers de revue séparés. Relancer `fold_measured.py` puis `build_proposal_geometry.py` puis le rendu dans cet ordre. La génération KiCad accepte `--geometry`, `--output` et `--name` pour préserver la carte précédente.
