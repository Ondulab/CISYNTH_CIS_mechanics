"""Apply only the explicitly measured optical insets to the main assembly."""
import sys,json
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
from PySide2.QtWidgets import QApplication
app=QApplication.instance() or QApplication([])
import FreeCAD as A,FreeCADGui as G,Part
G.showMainWindow();here=Path(__file__).resolve().parent
d=A.openDocument(str(here.parent/'assemblage_v4.0.0.FCStd'));o=d.TBV4_ActiveArea
# Local Display frame: front view with connectors left has top at local Y=0.
o.Placement=A.Placement();o.Shape=Part.makePlane(251,8.3,A.Vector(10.5,1.5,-.005));o.Label='Zone OLED — retraits mesures 10,5 / 1,2 / 1,5 / 1 mm';o.LongueurActive=251;o.HauteurActive=8.3;o.Validation='Cotes utilisateur du 09/09/2026, dimensions 251 x 8,3 mm'
for n,value in [('RetraitGauche',10.5),('RetraitDroit',1.2),('RetraitHaut',1.5),('RetraitBas',1.)]:
 if n not in o.PropertiesList:o.addProperty('App::PropertyLength',n,'Dimensions mesurees')
 setattr(o,n,value)
o.Visibility=True;d.recompute();d.save()
print('Updated measured optical area; PCB and original placement unchanged')
