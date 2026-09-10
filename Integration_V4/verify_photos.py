"""Check saved CAD frames, all source solids, developed volume and KiCad outline.
Run after generating Photos_2026-09-10 and exporting board-only STEP to
/tmp/photos_board.step with KiCad --user-origin 50x68mm.
"""
import sys,json,zipfile,xml.etree.ElementTree as E
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
here=Path(__file__).resolve().parent;out=here/'Photos_2026-09-10'
d=A.openDocument(str(out/'TouchBar_Montage_Photos.FCStd'));full=A.openDocument(str(out/'assemblage_v4.0.0_montage_ecran.FCStd'));source=A.openDocument(str(here.parent/'assemblage_v4.0.0.FCStd'))
plan=json.loads((out/'fold_plan.json').read_text());report={}
def gs(o):s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
def pcbframe(o):s=gs(o);s.translate(A.Vector(23.9,3.77,0));return s
for key in ['Touch','Display']:
 assert plan['checks'][key]['volume_relative_error']<.0001
 for typ in ['Flex','Blindage','Connecteur']:
  s=d.getObject(key+'_'+typ).Shape;assert s.isValid()
  assert len(s.Solids)==1,(key,typ)
for item in plan['checks']['between_ribbons'].values():assert item['overlap_mm3']<1e-7
pcb=d.PCB_Propose.Shape;report['pcb_valid']=pcb.isValid();assert pcb.isValid() and len(pcb.Solids)==1
preserved=[]
for old in source.Objects:
 if old.Name.startswith('TBV4'):continue
 new=full.getObject(old.Name);assert new is not None,old.Name
 assert new.TypeId==old.TypeId,old.Name
 if hasattr(old,'Placement') and old.Name!='Part008':assert old.Placement==new.Placement,old.Name
 if 'Sketch' in old.TypeId:
  assert old.GeometryCount==new.GeometryCount and old.ConstraintCount==new.ConstraintCount,old.Name
  assert all(str(a)==str(b) for a,b in zip(old.Geometry,new.Geometry)),old.Name
 if old.TypeId=='PartDesign::Body':assert abs(old.Shape.Volume-new.Shape.Volume)<1e-6,old.Name
 preserved.append(old.Name)
report['preserved_source_objects']=len(preserved)
report['saved_cad_alignment']={}
for name,ref in [('PCB_Photos','PCB_Propose'),('TBV4_MIPI_Flex','Display_Flex'),('TBV4_Touch_Flex','Touch_Flex'),('TBV4_J1_Socket','J1_Socket'),('TBV4_J2_Socket','J2_Socket'),('TBV4_J1_Plug','Display_Connecteur'),('TBV4_J2_Plug','Touch_Connecteur'),('TBV4_J4_Envelope','RJ45')]:
 a=pcbframe(full.getObject(name));b=d.getObject(ref).Shape
 residual=max(abs(getattr(a.BoundBox,k)-getattr(b.BoundBox,k)) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax']);assert residual<1e-7,(name,residual)
 report['saved_cad_alignment'][name]=residual
# Compare geometry to all physical leaf solids from the current source assembly.
# Parent placement changes only for PCB; other CAD construction objects are kept.
obstacles=[]
gui=E.fromstring(zipfile.ZipFile(here.parent/'assemblage_v4.0.0.FCStd').read('GuiDocument.xml'))
visible={o.get('name'):o.find(".//Property[@name='Visibility']/Bool").get('value')=='true' for o in gui.findall('.//ViewProvider') if o.find(".//Property[@name='Visibility']/Bool") is not None}
def hidden_parent(o):
 while hasattr(o,'getParentGeoFeatureGroup'):
  o=o.getParentGeoFeatureGroup()
  if o is None:return None
  if not visible.get(o.Name,True):return o.Name
 return None
for o in source.Objects:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Shape.Volume<1e-8:continue
 if o.Name.startswith('TBV4') or o.Name in ['Body023','Body025']:continue
 if o.TypeId=='PartDesign::Body' or (o.TypeId=='Part::Feature' and not any(p.TypeId=='PartDesign::Body' for p in o.InList)):
  obstacles.append((o.Name,o.Label,pcbframe(o),hidden_parent(o)))
report['against_source_solids']={};report['hidden_reference_collisions']={}
for name in ['PCB_Propose','Touch_Flex','Touch_Blindage','Touch_Connecteur','Display_Flex','Display_Blindage','Display_Connecteur','J1_Socket','J2_Socket','RJ45']:
 s=d.getObject(name).Shape;collisions=[];hidden=[]
 for oname,label,shape,hidden_by in obstacles:
  if s.BoundBox.intersect(shape.BoundBox):
   volume=s.common(shape).Volume
   if volume>1e-6:
    entry=dict(object=oname,label=label,volume_mm3=volume)
    if hidden_by:entry['hidden_ancestor']=hidden_by;hidden.append(entry)
    else:collisions.append(entry)
 report['against_source_solids'][name]=collisions;report['hidden_reference_collisions'][name]=hidden
 assert not collisions,(name,collisions)
# Compare generated PCB face including both RJ45 NPTH holes and CIS opening.
k=Part.read('/tmp/photos_board.step');face=max(k.Faces,key=lambda f:f.Area);top=max(pcb.Faces,key=lambda f:f.Area)
report['pcb_area_freecad_mm2']=top.Area;report['pcb_area_kicad_mm2']=face.Area
report['pcb_area_difference_mm2']=abs(face.Area-top.Area);assert abs(face.Area-top.Area)<.0001
report['kicad_bbox']=str(k.BoundBox)
# Project the two planar faces into the same XY plane, then compare their overlap.
a=face.copy();a.translate(A.Vector(0,0,-a.BoundBox.ZMin));b=top.copy();b.translate(A.Vector(0,0,-b.BoundBox.ZMin))
report['pcb_face_difference_mm2']=a.cut(b).Area+b.cut(a).Area;assert report['pcb_face_difference_mm2']<.0001
# Export all components together; this also checks that the mechanical model
# appears in KiCad and that every local connector model uses the same frame.
elec=here.parent.parents[1]/'Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/Montage_Photos'
assembled=Part.read(str(elec/'CIS_Montage_Photos.step'))
report['kicad_model_roundtrip']={}
# KiCad's STEP model datum is 0.995 mm above the underside for this 1 mm board.
zshift=.995-(plan['board_bottom_global_z']+1)
for name in ['Ecran','Touch_Flex','Touch_Blindage','Touch_Connecteur','Display_Flex','Display_Blindage','Display_Connecteur','J1_Socket','J2_Socket','RJ45']:
 expected=d.getObject(name).Shape.copy();expected.translate(A.Vector(0,0,zshift))
 def error(candidate):return max(abs(getattr(candidate.BoundBox,k)-getattr(expected.BoundBox,k)) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax'])
 actual=min(assembled.Solids,key=error);residual=error(actual);assert residual<.00001,(name,residual)
 assert abs(actual.Volume-expected.Volume)<.0001,(name,actual.Volume,expected.Volume)
 report['kicad_model_roundtrip'][name]=dict(bbox_residual_mm=residual,volume_residual_mm3=abs(actual.Volume-expected.Volume))
report['kicad_model_z_datum_mm']=.995
report['checked_source_obstacles']=len(obstacles)
report['adoption_status']='Nominal CAD only; scan registration, small bend radius, J2 footprint and PCB mounting changes require physical validation.'
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
