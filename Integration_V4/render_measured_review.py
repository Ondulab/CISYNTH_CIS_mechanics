import sys,json,time
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
from PySide2.QtWidgets import QApplication
app=QApplication.instance() or QApplication([])
import FreeCAD as A,FreeCADGui as G,Part
from fold_measured import make_routes,data
G.showMainWindow();G.getMainWindow().resize(1600,900);here=Path(__file__).resolve().parent
d=A.openDocument(str(here/'TouchBar_Scans_Proposition.FCStd'));routes,_=make_routes()
for o in list(d.Objects):
 if o.Name.startswith('Interference_') or 'MetalVisible' in o.Name:d.removeObject(o.Name)
# Annotate actual nominal interference solids in the proposal.
for first,second in [('Touch_Flex','Display_Flex'),('Touch_Flex','Coque_Reference'),('Touch_Blindage','Coque_Reference'),('Display_Flex','Coque_Reference'),('Display_Blindage','Coque_Reference')]:
 overlap=d.getObject(first).Shape.common(d.getObject(second).Shape)
 if overlap.Volume>1e-7:
  o=d.addObject('Part::Feature','Interference_'+first+'_'+second);o.Shape=overlap;o.ViewObject.ShapeColor=(1.,.05,.03);o.Label='INTERFERENCE '+first+' / '+second
for key in ['Touch','Display']:
 g=data[key];u0,v0,u1,v1=g['metal_uv_bounds_mm'];route=routes[key];n=g['metal_total_thickness_mm']-data['flex_thickness_mm']/2+.003
 pts=[route.point(u,v,n) for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
 o=d.addObject('Part::Feature',key+'_MetalVisible');o.Shape=Part.Face(Part.makePolygon(pts+[pts[0]]));o.ViewObject.ShapeColor=(.67,.69,.72)
for o in d.Objects:
 if hasattr(o,'Shape'):
  o.Visibility=True
  if 'Interference' in o.Name:continue
  o.ViewObject.LineColor=(.08,.08,.08)
  if 'Flex' in o.Name:o.ViewObject.ShapeColor=(.12,.12,.14);o.ViewObject.Transparency=50
  elif 'Blindage' in o.Name:o.ViewObject.ShapeColor=(.2,.2,.22)
  elif 'Connecteur' in o.Name:o.ViewObject.ShapeColor=(.77,.64,.27)
  elif 'PCB' in o.Name:o.ViewObject.ShapeColor=(.18,.42,.28);o.ViewObject.Transparency=65
  elif o.Name=='ZoneActive':o.ViewObject.ShapeColor=(.03,.24,.32)
  elif o.Name=='Ecran':o.ViewObject.ShapeColor=(.025,.025,.03)
  if 'Deplie' in o.Name or o.Name in ['CIS_Reference','PCB_Original','Coque_Reference']:o.Visibility=False
# Keep original whole geometry in the native document; clip only for screenshots.
d.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();d.save()
Part.export([o for o in d.Objects if hasattr(o,'Shape') and o.Visibility],str(here/'TouchBar_Scans_Proposition.step'))
clip=Part.makeBox(78,25,25,A.Vector(-3,-3,-10))
for o in d.Objects:
 if hasattr(o,'Shape') and o.Visibility:o.Shape=o.Shape.common(clip)
d.RJ45.Visibility=False
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
for _ in range(10):app.processEvents();time.sleep(.05)
G.activeDocument().activeView().saveImage(str(here/'nappes_scans_proposition.png'),1600,850,'White')
A.closeDocument(d.Name)
