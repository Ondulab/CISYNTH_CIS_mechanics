"""Checks actual saved solids and preservation of original feature geometry.
Run after extracting the checkpoint to /tmp/sp3ctra-before.FCStd and exporting
KiCad board-only STEP to /tmp/sp3ctra-board.step (see README).
"""
import sys,json
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
here=Path(__file__).resolve().parent
d=A.openDocument(str(here.parent/'assemblage_v4.0.0.FCStd'));old=A.openDocument('/tmp/sp3ctra-before.FCStd')
def gs(o):s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
preserved=[]
for o in old.Objects:
 n=d.getObject(o.Name);assert n is not None,o.Name
 assert n.Placement==o.Placement if hasattr(o,'Placement') else True,o.Name
 if 'Sketch' in o.TypeId:
  assert o.GeometryCount==n.GeometryCount and o.ConstraintCount==n.ConstraintCount,o.Name
  assert all(str(a)==str(b) for a,b in zip(o.Geometry,n.Geometry)),o.Name
 if o.TypeId in ['PartDesign::Body','PartDesign::Pad','PartDesign::Pocket']:
  assert abs(o.Shape.Volume-n.Shape.Volume)<1e-6,o.Name
  assert gs(o).distToShape(gs(n))[0]<1e-7,o.Name
  preserved.append(o.Name)
for o in d.Objects:
 if o.Name.startswith('TBV4_'):assert not o.Shape.isNull() and o.Shape.isValid(),o.Name
shell=gs(d.Body022);pcb=gs(d.Body025);cis=gs(d.Body)
checks={}
for name in ['TBV4_MIPI_Flex','TBV4_Touch_Flex']:
 s=gs(d.getObject(name));checks[name]={}
 for label,other in [('coque',shell),('PCB',pcb),('CIS',cis)]:
  overlap=s.common(other).Volume;clearance=s.distToShape(other)[0]
  assert overlap<1e-7,(name,label,overlap)
  checks[name][label]={'overlap_mm3':overlap,'clearance_mm':clearance}
 assert len(s.Solids)==1
checks['original_features_preserved']=len(preserved)
# Independent KiCad STEP import checks dimensions; NPTH holes intentionally differ.
k=Part.read('/tmp/sp3ctra-board.step');bb=k.BoundBox
assert abs(bb.XLength-256)<.001 and abs(bb.YLength-18)<.001,str(bb)
checks['kicad_step_bounds_mm']=[bb.XLength,bb.YLength,bb.ZLength]
face=max(k.Faces,key=lambda f:f.Area)
area=Part.Face(face.OuterWire).Area
assert abs(area-d.Body025.Shape.Volume)<.0001, (area,d.Body025.Shape.Volume)
checks['kicad_outline_area_mm2']=area
checks['kicad_board_area_with_NPTH_mm2']=face.Area
checks['kicad_step_note']='Board-only STEP represents 0.91 mm dielectric; declared finished thickness is 1 mm (Cu + mask excluded by export).'
checks['freecad_outline_area_mm2']=d.Body025.Shape.Volume
(here/'verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
