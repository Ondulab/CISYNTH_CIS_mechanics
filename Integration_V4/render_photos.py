"""Colour the nominal assembly, export KiCad mechanics, and save a full CAD variant.
The source assembly remains the checkpoint; only the variant PCB is adapted.
"""
import sys,json,time,re
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
from PySide2.QtWidgets import QApplication
app=QApplication.instance() or QApplication([])
import FreeCAD as A,FreeCADGui as G,Part,Sketcher
from fold_photos import make_routes,data,OUT,here
def zoom(view,factor):
 camera=view.getCamera();camera=re.sub(r'height\s+([0-9.eE+-]+)',lambda m:'height '+str(float(m.group(1))*factor),camera);view.setCamera(camera)
G.showMainWindow();G.getMainWindow().resize(1600,900)
d=A.openDocument(str(OUT/'TouchBar_Montage_Photos.FCStd'));routes,_=make_routes();g=json.loads((OUT/'geometry.json').read_text());original=json.loads((here/'geometry.json').read_text());plan=json.loads((OUT/'fold_plan.json').read_text())
for o in list(d.Objects):
 if o.Name.startswith(('J1_Socket','J2_Socket')) or 'MetalVisible' in o.Name:d.removeObject(o.Name)
source=A.openDocument(str(here.parent/'assemblage_v4.0.0.FCStd'))
def gs(o):s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
# Socket envelopes are the same dimensions as KiCad's local model files.
for ref in ['J1','J2']:
 shape=gs(source.getObject('TBV4_'+ref+'_Socket'));ox,oy=original['connectors'][ref]['center'];nx,ny=g['connectors'][ref]['center'];shape.translate(A.Vector(23.9+nx-ox,3.77+ny-oy,plan['pcb_raise_mm']))
 o=d.addObject('Part::Feature',ref+'_Socket');o.Shape=shape
for key in ['Touch','Display']:
 q=data[key];u0,v0,u1,v1=q['metal_uv_bounds_mm'];route=routes[key];n=q['metal_total_thickness_mm']-data['flex_thickness_mm']/2+.003
 pts=[route.point(u,v,n) for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
 o=d.addObject('Part::Feature',key+'_MetalVisible');o.Shape=Part.Face(Part.makePolygon(pts+[pts[0]]));o.ViewObject.ShapeColor=(.70,.72,.75)
for o in d.Objects:
 if not hasattr(o,'Shape'):continue
 o.Visibility=True;o.ViewObject.LineColor=(.07,.07,.08)
 if 'Flex' in o.Name:o.ViewObject.ShapeColor=(.12,.12,.15)
 elif 'Blindage' in o.Name:o.ViewObject.ShapeColor=(.2,.2,.23)
 elif 'Connecteur' in o.Name:o.ViewObject.ShapeColor=(.78,.65,.30)
 elif 'Socket' in o.Name:o.ViewObject.ShapeColor=(.14,.14,.16)
 elif 'PCB' in o.Name:o.ViewObject.ShapeColor=(.12,.42,.27);o.ViewObject.Transparency=60
 elif o.Name=='ZoneActive':o.ViewObject.ShapeColor=(.03,.24,.32)
 elif o.Name=='Ecran':o.ViewObject.ShapeColor=(.025,.025,.035)
 elif o.Name=='RJ45':o.ViewObject.ShapeColor=(.65,.68,.71)
 elif o.Name=='Coque_Reference':o.ViewObject.ShapeColor=(.65,.68,.70);o.ViewObject.Transparency=85
 if 'Deplie' in o.Name or o.Name in ['CIS_Reference','PCB_Original','Coque_Reference']:o.Visibility=False
A.setActiveDocument(d.Name);d.recompute();view=G.activeDocument().activeView();view.viewAxonometric();view.fitAll();d.save()
Part.export([o for o in d.Objects if hasattr(o,'Shape') and o.Visibility],str(OUT/'TouchBar_Montage_Photos.step'))
# Export optical face + flexes + plugs into a mechanical footprint at PCB local 0,0.
# Model z=0 is the finished front copper face; y remains the CAD upward axis.
elec=here.parent.parents[1]/'Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/Montage_Photos';modeldir=elec/'models';modeldir.mkdir(parents=True,exist_ok=True)
md=A.newDocument('KiCad_TouchBar_Model');include=['Ecran','ZoneActive']+[k+'_'+t for k in ['Touch','Display'] for t in ['Flex','Blindage','Connecteur','MetalVisible']]
for name in include:
 src=d.getObject(name);s=src.Shape.copy();s.translate(A.Vector(0,0,-(plan['board_bottom_global_z']+1)));o=md.addObject('Part::Feature',name);o.Shape=s;o.ViewObject.ShapeColor=src.ViewObject.ShapeColor
Part.export(md.Objects,str(modeldir/'TouchBar_folded.step'));A.closeDocument(md.Name)
# Full editable source assembly variant: retain every original construction object.
source.Label='Assemblage V4 — montage écran photos, PCB +1,6 mm'
source.Part008.Placement.Base.z=plan['board_bottom_global_z']
def assign(parent,name,review_name,label):
 o=source.getObject(name) or source.addObject('Part::Feature',name)
 if o not in parent.Group:parent.addObject(o)
 s=d.getObject(review_name).Shape.copy();s.translate(A.Vector(-23.9,-3.77,0));s.transformShape(parent.getGlobalPlacement().inverse().toMatrix());o.Shape=s;o.Label=label
 o.ViewObject.ShapeColor=d.getObject(review_name).ViewObject.ShapeColor;o.Visibility=True
 if 'Validation' not in o.PropertiesList:o.addProperty('App::PropertyString','Validation')
 o.Validation='Montage nominal photos ; paramètres et limites dans Photos_2026-09-10/README.md'
 # Check the saved parent placement maps the object back to the review exactly.
 expected=d.getObject(review_name).Shape.copy();expected.translate(A.Vector(-23.9,-3.77,0));actual=gs(o)
 assert actual.distToShape(expected)[0]<1e-7,name
 assert abs(actual.BoundBox.XMin-expected.BoundBox.XMin)<1e-7,name
 return o
# Native sketch + pad retain an editable PCB in the full assembly variant.
body=source.addObject('PartDesign::Body','PCB_Photos');source.Part008.addObject(body);body.Placement=A.Placement();body.Label='PCB — variante photos, contour éditable'
sketch=body.newObject('Sketcher::SketchObject','PCB_Photos_Contour')
for edge in g['edges']:
 pts=[A.Vector(x,y,0) for x,y in edge['points']]
 curve=Part.LineSegment(pts[0],pts[2]) if edge['type']=='line' else Part.Arc(pts[0],pts[1],pts[2])
 sketch.addGeometry(curve,False)
for hole in g['footprint_drills']:sketch.addGeometry(Part.Circle(A.Vector(hole['x'],hole['y'],0),A.Vector(0,0,1),hole['diameter']/2),False)
pad=body.newObject('PartDesign::Pad','PCB_Photos_Epaisseur');pad.Profile=sketch;pad.Length=1;source.recompute();sketch.Visibility=False
assert pad.Shape.isValid() and abs(pad.Shape.Volume-d.PCB_Propose.Shape.Volume)<1e-5
body.ViewObject.ShapeColor=(.12,.42,.27);pad.ViewObject.ShapeColor=(.12,.42,.27)
for ref,w,h in [('J1',8.55,1.7),('J2',3.8,7.2)]:
 cx,cy=g['connectors'][ref]['center'];marker=source.addObject('Sketcher::SketchObject',ref+'_Implantation_Photos');source.Part008.addObject(marker);marker.Placement=A.Placement(A.Vector(0,0,1),A.Rotation())
 pts=[A.Vector(x,y,0) for x,y in [(cx-w/2,cy-h/2),(cx+w/2,cy-h/2),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2)]]
 for a,b in zip(pts,pts[1:]+pts[:1]):marker.addGeometry(Part.LineSegment(a,b),False)
 marker.Label=ref+' — emplacement nominal synchronisé KiCad';marker.Visibility=False
source.Body025.Visibility=False
for ref,key in [('J1','Display'),('J2','Touch')]:
 assign(source.Part008,'TBV4_'+ref+'_Socket',ref+'_Socket',ref+' — embase '+key+' nominale')
 assign(source.Part025,'TBV4_'+ref+'_Plug',key+'_Connecteur',ref+' — connecteur nappe '+key)
 assign(source.Part025,'TBV4_'+('MIPI' if key=='Display' else 'Touch')+'_Flex',key+'_Flex','Nappe '+key+' — 0,150 mm, plis au bord')
 assign(source.Part025,'TBV4_'+key+'_Blindage',key+'_Blindage',key+' — enveloppe composants et blindage')
 assign(source.Part025,'TBV4_'+key+'_MetalVisible',key+'_MetalVisible',key+' — surface métallique relevée')
 source.getObject('TBV4_'+ref+'_Pads').Visibility=False
 source.getObject('Sketch087' if ref=='J1' else 'Sketch086').Visibility=False
assign(source.Part008,'TBV4_J4_Envelope','RJ45','J4 — Ethernet en bord de PCB')
source.recompute();A.setActiveDocument(source.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();source.saveAs(str(OUT/'assemblage_v4.0.0_montage_ecran.FCStd'));A.closeDocument(source.Name)
# Review images crop only the temporary scene, after saving full models above.
A.setActiveDocument(d.Name);clip=Part.makeBox(65,24,22,A.Vector(-2,-3,-10))
for o in d.Objects:
 if hasattr(o,'Shape') and o.Visibility:o.Shape=o.Shape.common(clip)
d.RJ45.Visibility=False
view=G.activeDocument().activeView();view.viewAxonometric();view.fitAll();zoom(view,.6)
for _ in range(15):app.processEvents();time.sleep(.05)
view.saveImage(str(OUT/'detail_nappes.png'),1600,850,'White')
view.viewFront();view.fitAll();zoom(view,.55)
for _ in range(15):app.processEvents();time.sleep(.05)
view.saveImage(str(OUT/'profil_plis.png'),1600,650,'White')
view.viewTop();view.fitAll();zoom(view,.55)
for _ in range(15):app.processEvents();time.sleep(.05)
view.saveImage(str(OUT/'implantation_nappes.png'),1600,700,'White')
A.closeDocument(d.Name)
print('Saved coloured assembly, full CAD variant, STEP and KiCad model')
