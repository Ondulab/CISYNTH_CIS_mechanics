# CIS WHEC — relevé préalable à la reprise Part Design

État au 9 septembre 2026 : collecte terminée ; aucune modification du fichier FreeCAD partagé à ce stade. Attente de la fin de l'autre instance, conformément à la demande utilisateur. Des écritures de l'autre travail ont été observées dans `Integration_V4` pendant le relevé.

## Sources et portée

- **WHEC LC3R216N-8008**, document **HHIK-8008A**, révision A du **18 décembre 2023**, figure 1, page 14/14. Copie locale : [fiche WHEC](sources/LC3R216N-8008A.pdf), [plan agrandi](sources/WHEC_Figure1_page14.png). Le nom du fichier finit par `8008A` : le A est la révision documentaire ; la référence imprimée du module est `LC3R216N-8008`.
- Le fabricant marque cette fiche **Preliminary** et précise qu'il ne s'agit pas d'une spécification finale. Les valeurs ci-dessous sont certaines comme lecture de cette édition, mais la conformité de l'exemplaire physique à cette édition reste à confirmer.
- [JST, plan de famille FLZ](https://www.jst.fr/core/file.get?path=doc/jst/family/pdf/eflz0125.pdf), pages 1 à 3, consulté le 9 septembre 2026 ; [copie locale](sources/JST_FLZ_eflz0125.pdf). Ce document donne le FLZ RSM2 standard ; il ne certifie pas à lui seul l'enveloppe de chaque variante GAN ou d'un équivalent monté par WHEC.
- Modèle examiné en lecture seule : `../assemblage_v4.0.0.FCStd`, groupe `Part / CIS`, corps `Body / Corps_CIS`, `Body001 / PCB_CIS`, `Body002 / Vitre`, connecteur importé `Part__Feature210 / _30481210_cp`.
- Les fichiers `../BOM/CIS/M118-232C3*.pdf` concernent **un autre fabricant et un autre module**, avec un connecteur 12 broches. Ils ne doivent pas servir à certifier les détails internes du WHEC.

Les copies des sources et leurs empreintes SHA-256 sont enregistrées dans `sources/provenance.json`.

## Repère proposé pour conserver l'orientation du CIS existant

X : longueur, de l'extrémité opposée au connecteur vers l'extrémité proche du connecteur. Y : largeur ; Y=0 du côté le plus proche de la ligne de lecture. Z : du dos du boîtier vers la face de verre. Dans ce repère, la face de verre est à Z=11,7 et les axes des trous sont parallèles à X. Le premier pixel utile est du côté X élevé, puis la lecture se fait vers X décroissant.

Le placement existant du groupe CIS est **(1,19 ; −3,76 ; −1,30) mm**, sans rotation. Il s'agit d'un placement d'assemblage utilisateur, pas d'une cote WHEC. Son maintien ou son ajustement doit être évalué après la fin des éditions concurrentes, à partir du fichier alors courant.

## Cotes explicitement portées sur le plan WHEC

Toutes les longueurs sont en mm. Une absence de tolérance ne signifie jamais une tolérance nulle.

| Grandeur | Valeur du plan | Interprétation / conséquence |
|---|---:|---|
| Longueur extérieure | 232 ± 0,5 | Enveloppe X nominale 0 à 232 |
| Largeur extérieure | 18 ± 0,3 | Enveloppe Y nominale 0 à 18 |
| Hauteur, face de verre au dos du boîtier | 11,7 ± 0,3 | N'inclut pas la saillie du connecteur |
| Encombrement total en hauteur | MAX 14 | Limite supérieure, **pas une hauteur nominale de 14** |
| Épaisseur de la vitre | 1,8 | Mention `GLASS 1.8t`, tolérance non fournie |
| Nombre de trous de fixation | 2 × 2 | Deux trous dans chacune des deux extrémités |
| Diamètre des avant-trous | Ø2,2 | Tolérance non fournie ; pas un taraudage M2,2 |
| Profondeur des avant-trous | 6,5 | Trous borgnes axiaux, tolérance non fournie |
| Axe du premier trou depuis le bord latéral | 1,8 ± 0,2 | Y1=1,8 au nominal |
| Entraxe transversal des trous | 14,4 ± 0,2 | Y2=1,8+14,4=16,2 au nominal |
| Axe des trous depuis la face de verre | 8,3 ± 0,2 | Z=11,7−8,3=3,4 au nominal |
| Longueur utile de lecture | 216 | Sans tolérance géométrique explicite |
| Début utile depuis l'extrémité proche du connecteur | 8 ± 0,5 | X du début utile = 232−8=224 au nominal ; 41e pixel à 600 dpi |
| Ligne de lecture depuis le bord latéral | 5,5 ± 0,5 | Y=5,5 au nominal |
| Plan de lecture au-dessus de la vitre | 0,45 | Repère optique, **pas une couche solide de 0,45** ; tolérance non fournie |
| Taille du chanfrein, détail A | 0,4 ± 0,15 | Mesure verticale montrée au détail A |
| Angle du chanfrein | 45° ± 5° | Étendue exacte du traitement autour de la vitre à confirmer |
| Vis recommandées | M2,5 (M2,6) autotaraudeuses | Longueur, tête et engagement effectif non spécifiés |
| Connecteur | 18FLZ-RSM2-GAN-TB(LF) ou équivalent | 18 contacts, ne correspond pas à l'ancien import 12 broches |

La vitre ne doit pas dépasser les bords latéraux du cadre (note 4). Le plan ne définit pas un jeu latéral nominal chiffré.

## Cotes calculées, à ne pas confondre avec des cotes indépendantes

| Grandeur | Nominal | Limite de l'interprétation |
|---|---:|---|
| Second axe de trou Y2 | 16,2 | Somme de 1,8 et 14,4 ; somme des tolérances ±0,4 si indépendantes |
| Recul du second axe depuis l'autre bord | 1,8 | 18−1,8−14,4 ; cumul maximal ±0,7 si indépendant, pas un second ±0,2 garanti |
| Hauteur des axes depuis le dos | 3,4 | 11,7−8,3 ; cumul maximal ±0,5 si indépendant |
| Sous-face de verre depuis le dos | 9,9 | 11,7−1,8 ; tolérance inconnue sur l'épaisseur de verre |
| Début de ligne utile X | 224 | 232−8 ; cumul maximal ±1,0 si indépendant |
| Fin de ligne utile X | 8 | 232−8−216 ; tolérance de 216 non spécifiée |
| Plan de lecture Z | 12,15 | 11,7+0,45 ; tolérance sur la distance optique non spécifiée |
| Saillie maximale disponible sous le dos nominal | 2,3 | 14−11,7 ; varie avec la hauteur réelle du module |

Les chaînes de tolérances sont des calculs conservatifs, pas des prescriptions de WHEC.

## Connecteur : informations complémentaires JST

Le FLZ RSM2 standard 18 contacts est donné pour un pas de **0,5**, une portée entre premiers et derniers contacts **A=8,5**, une largeur totale **B=14,9**, une hauteur de montage **2**, une profondeur fermée **4,6**, avec une saillie arrière de contacts indiquée **(0,7)**. La profondeur en position ouverte est donnée **(6,4)**. Les cotes entre parenthèses sont des indications de référence. Le catalogue indique un contact sur la face inférieure pour la version reverse. L'épaisseur à l'extrémité de la FFC/FPC est **0,3 ± 0,03** (cela ne fixe pas l'épaisseur de toute une nappe).

Ces dimensions documentent une enveloppe de famille. La position X/Y/Z du composant sur le module, la variante réellement livrée et l'encombrement de son verrou ouvert restent à confirmer. Aucune nappe WHEC n'est cotée en longueur ou en cheminement par le plan.

## Écarts du modèle FreeCAD existant

| Élément | Modèle examiné | WHEC / action nécessaire |
|---|---|---|
| Longueur du corps | 231 | 232 nominal |
| Largeur du corps | 18 | 18 nominal, tolérance à conserver en documentation |
| Sommet du corps / sommet vitre | 11,3 / 11,8 | Face de verre 11,7 ; répartition corps/verre à reconstruire |
| Vitre | 228,8 × 15,8 × 2 ; X/Y=1,1 ; Z=9,8 | Épaisseur 1,8 certaine ; longueur/largeur et retraits non cotés WHEC |
| PCB interne | 228,8 × 15,8 × 1 ; X/Y=1,1 ; Z=0 | Toutes ces cotes internes restent non confirmées pour WHEC |
| Trous | Ø2,4, Y=2 et 16, Z=4,9 ; coupe traversante | Ø2,2, Y=1,8 et 16,2, Z=3,4 ; quatre poches borgnes de 6,5 |
| Cavités optiques internes | Profils détaillés hérités, multiples cotes | Aucun plan en coupe WHEC permettant de les certifier |
| Connecteur | Import 12 contacts, boîte englobante 16,75 × 5,5 × 5,811 environ | Remplacer par un 18 contacts ; ne pas réutiliser cette géométrie comme WHEC |
| Ligne / plan de lecture | Pas de repère WHEC explicite identifié | Ajouter des repères non volumiques aux coordonnées documentées |

## Toutes les incertitudes à restituer

1. **Révision physique** : confirmer que le module détenu correspond au LC3R216N-8008 décrit par HHIK-8008A préliminaire.
2. **Vitre, longueur et largeur** : aucune cote nominale ni tolérance ; les retraits des quatre côtés ne sont pas cotés. Les 1,1 mm du modèle ancien ne sont pas des cotes WHEC.
3. **Vitre, épaisseur** : nominal 1,8 documenté, tolérance et colle non spécifiées. Planéité, éventuel retrait/affleurement du cadre et épaisseur de collage inconnus.
4. **Chanfrein** : taille et angle cotés, mais aucune désignation explicite des quatre arêtes ni des coins ; ne pas garantir par extrapolation un chanfrein identique sur tout le pourtour.
5. **Cadre interne** : épaisseurs des parois et des extrémités, appuis de verre, cavités, nervures, arrondis, dépouilles, clips et découpes non cotés.
6. **PCB interne** : longueur, largeur, épaisseur, emplacement Z, débord du dos, fixation, contour et tolérances non cotés.
7. **Optique interne** : dimensions et positions de la barrette de lentilles, du guide lumineux, des LED, des puces et des masques non cotées. La longueur utile 216 ne définit pas la largeur physique de la fente optique.
8. **Connecteur, référence effective** : WHEC autorise un équivalent ; la fiche JST consultée ne constitue pas un plan spécifique du module assemblé.
9. **Connecteur, position** : recul à l'extrémité X, position Y, orientation exacte du verrou et hauteur Z de soudure non cotés. Une mesure à l'échelle du dessin serait seulement une estimation graphique.
10. **Connecteur, détails** : forme du verrou, contacts, renforts, jeux d'insertion, course et dégagement nécessaires non certifiés pour le composant réellement livré.
11. **Nappe WHEC** : longueur, largeur extérieure réelle, raidisseur, épaisseur hors zone de contact, orientation, rayons de pliage et cheminement inconnus.
12. **Perçages** : diamètre et profondeur nominaux documentés, mais tolérances, forme du fond, amorce/conicité et axe angulaire non spécifiés. Ne pas inventer de filet interne.
13. **Fixation assemblée** : longueur de vis, engagement, diamètre et position des supports du boîtier final à réévaluer ; les supports actuels ne deviennent pas conformes automatiquement en corrigeant le CIS.
14. **Lecture** : tolérance sur 216 et sur 0,45, épaisseur de ligne active et corrélation avec les tolérances extérieures non données. Le dessin cote Y=5,5 ; la largeur des traits du dessin ne cote pas une ouverture.
15. **Encombrement complet** : MAX 14 est une limite ; le partage entre PCB, soudure et connecteur n'est pas déterminé. Ne pas imposer 14 comme dimension nominale réelle.
16. **Repère d'intégration** : placement utilisateur existant connu, mais recalage sur les supports, la vitre externe et les nappes à vérifier sur l'assemblage après les modifications concurrentes.
17. **Tolérances d'ensemble** : pas de tolérance générale, de perpendicularité ou de planéité fournie ; toutes les cotes non tolérancées restent à confirmer pour une validation de fabrication.

Une maquette peut respecter les cotes nominales documentées et rendre les hypothèses modifiables. Elle ne peut pas être présentée comme une reproduction métrologique parfaite sans les données manquantes.

## Préparation conservée, non exécutée

`preparation_partdesign.py` contient la préparation de la reconstruction. Sa syntaxe Python est vérifiée ; **aucun solide de cette préparation n'a été généré ni validé**, et le point d'entrée refuse volontairement de lancer la construction. Le contrôle de fin de l'autre tâche, le chargement de la version définitive et les vérifications géométriques restent à effectuer avant utilisation.

Les choix provisoires préparés sont : verre de même enveloppe en plan que le cadre (232 × 18, retrait 0), chanfrein nominal 0,4 à 45° sur les quatre arêtes hautes ; cavité centrale avec parois latérales de 1 et extrémités de 7,5 ; logement arrière de 1,3 ; PCB de 229,8 × 15,8 × 1, retrait 1,1 et dos Z=0 ; connecteur représenté par une enveloppe fermée 14,9 × 5,3 × 2, centre X=208 et Y=11,7, Z de −2 à 0. **Ces valeurs ne deviennent pas des cotes WHEC par leur présence dans le script.** En particulier, le centre du connecteur est estimé graphiquement et l'interprétation du côté Y doit être confirmée. Une construction ultérieure doit reprendre et vérifier ces choix, qui ne sont pas encore un résultat CAO livré.

L'audit initial en lecture seule est conservé dans `etat_initial_releve.json`. Il révèle un risque d'interférence à droite : à placement CIS constant, une longueur 232 donne Xmax=233,19, tandis que l'enveloppe du support commence à X=232,30. Le recouvrement des boîtes englobantes de 0,89 **n'est pas une mesure d'intersection des solides**. La vitre WHEC se trouverait à Z global 10,40 au lieu de 10,50 précédemment ; les axes des fixations seraient à Z global 2,10 au lieu de 3,60. Ces changements nécessitent de contrôler les supports et la visserie après construction.

## Reprise prévue après libération des fichiers

- Recharger la dernière version, en sauvegarder une copie datée et relever les empreintes des fichiers avant modification.
- Utiliser des corps Part Design, des esquisses contraintes et des fonctions Pad/Pocket/Chamfer, avec des paramètres nommés et réellement reliés aux dimensions.
- Séparer les paramètres constructeur des dimensions internes provisoires et des repères optiques non matériels.
- Remplacer le sous-ensemble CIS, conserver les autres travaux et contrôler toute référence entrante avant remplacement.
- Contrôler dimensions, validité des solides, trous aux deux extrémités, absence de trou traversant, état de recalcul et réouverture du fichier enregistré.
- Comparer les géométries et placements hors CIS ; signaler les interférences nominales avec supports, vis et nappes sans inventer un jeu d'assemblage.
- Livrer un CIS autonome, son intégration à l'assemblage et un rapport des dimensions retenues, des hypothèses et des collisions éventuelles.
