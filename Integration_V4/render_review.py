import sys,json
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
from PySide2.QtWidgets import QApplication
app=QApplication.instance() or QApplication([])
import FreeCAD as A,FreeCADGui as G,Part
G.showMainWindow();G.getMainWindow().resize(1500,800)
here=Path(__file__).resolve().parent
d=A.openDocument(str(here/'Integration_TouchBar_V4.FCStd'))
d.Body022.Visibility=False
d.Body025.ViewObject.ShapeColor=(.16,.4,.28);d.Body023.ViewObject.ShapeColor=(.04,.045,.05)
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();app.processEvents()
G.activeDocument().activeView().saveImage(str(here/'vue_ensemble.png'),1800,650,'White')
clip=Part.makeBox(86,30,25,A.Vector(-25,-8,-11))
for o in d.Objects:
 if hasattr(o,'Shape'):o.Shape=o.Shape.common(clip)
d.TBV4_J4_Envelope.Visibility=False
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();app.processEvents()
G.activeDocument().activeView().saveImage(str(here/'detail_nappes.png'),1600,800,'White')
G.activeDocument().activeView().viewFront();G.activeDocument().activeView().fitAll();app.processEvents()
G.activeDocument().activeView().saveImage(str(here/'profil_plis.png'),1600,650,'White')
A.closeDocument(d.Name)
