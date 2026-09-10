import sys,json,math
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
here=Path(__file__).resolve().parent;out=here/'Photos_2026-09-10';source=A.openDocument(str(here.parent/'assemblage_v4.0.0.FCStd'));plan=json.loads((out/'fold_plan.json').read_text());g=json.loads((here/'geometry.json').read_text())
c=plan['notch']['center_x'];L=c-plan['notch']['width']/2;R=c+plan['notch']['width']/2;y=plan['notch']['bottom_y'];V=A.Vector
def seg(a,b):return Part.LineSegment(V(a[0],a[1],0),V(b[0],b[1],0))
def arc(x,y,a,b):return Part.ArcOfCircle(Part.Circle(V(x,y,0),V(0,0,1),1),a,b)
replacements={2:seg((255,18),(R+1,18)),34:seg((L,17),(L,y+1)),35:seg((L+1,y),(R-1,y)),36:seg((L-1,18),(26.4,18)),37:seg((R,y+1),(R,17)),38:arc(L-1,17,0,math.pi/2),40:arc(R+1,17,math.pi/2,math.pi),42:arc(L+1,y+1,math.pi,3*math.pi/2),44:arc(R-1,y+1,3*math.pi/2,2*math.pi)}
edges=[];geoms=[]
for i,orig in enumerate(source.Sketch085.Geometry):
 curve=replacements.get(i,orig)
 if isinstance(curve,Part.Point):continue
 e=curve.toShape();geoms.append(curve);p=[e.valueAt(t) for t in [e.FirstParameter,(e.FirstParameter+e.LastParameter)/2,e.LastParameter]];edges.append({'type':'arc' if isinstance(e.Curve,Part.Circle) else 'line','points':[[v.x,v.y] for v in p]})
g['edges']=edges;g['placement'][2]=plan['board_bottom_global_z'];g['status']='Montage nominal photos : recalage transversal -0.25 mm Display, PCB +1.6 mm, rayon neutre 0.2 mm a valider';g['board_note']='MONTAGE NOMINAL PHOTOS - NON ROUTE - VALIDATION PHYSIQUE REQUISE';g['notch']=plan['notch']
for ref,key in [('J1','Display'),('J2','Touch')]:
 g['connectors'][ref]['center']=plan['connectors'][key]['connector_xyz_mm'][:2];g['connectors'][ref]['angle']=plan['connectors'][key]['connector_rotation_deg'];g['connectors'][ref]['source']='scan + conservation longueur developpee';g['connectors'][ref]['former_sketch_center']=json.loads((here/'geometry.json').read_text())['connectors'][ref]['center']
g['mapping']='X=50+Xlocal; Y=68-Ylocal; F.Cu=Zglobal '+str(plan['board_bottom_global_z']+1)
g['connectors']['J2']['reference_position']=[28.5,14.6]
g['connectors']['J1']['pin1_silk_shift_mm']=[.8,0]
g['notch_keepout_margin_mm']=.2
g['mechanical_step_model']='models/TouchBar_folded.step'

w=Part.Wire(Part.__sortEdges__([c.toShape() for c in geoms]));assert w.isClosed();pcb=Part.Face(w).extrude(V(0,0,1));pcb.translate(V(0,0,plan['board_bottom_global_z']))
def gs(o):s=o.Shape.copy();s.Placement=o.getGlobalPlacement();s.translate(V(23.9,3.77,0));return s
shell=gs(source.Body022);cis=gs(source.Body)
cisparts=[gs(source.getObject(n)) for n in ['Body','Body001','Body002','Part__Feature210']]
cis=Part.makeCompound(cisparts)
# Raising the motherboard exposes an existing CIS connector beneath the sensor.
# A separate, explicit rounded access opening clears its full PCB-height envelope.
interference=pcb.common(cis);cutout=None
if interference.Volume>1e-7:
 bb=interference.BoundBox;clear=.35;rad=.5
 x0,x1,y0,y1=bb.XMin-clear,bb.XMax+clear,bb.YMin-clear,bb.YMax+clear
 def ra(x,y,a,b):return Part.ArcOfCircle(Part.Circle(V(x,y,0),V(0,0,1),rad),a,b)
 holes=[seg((x0+rad,y0),(x1-rad,y0)),ra(x1-rad,y0+rad,-math.pi/2,0),seg((x1,y0+rad),(x1,y1-rad)),ra(x1-rad,y1-rad,0,math.pi/2),seg((x1-rad,y1),(x0+rad,y1)),ra(x0+rad,y1-rad,math.pi/2,math.pi),seg((x0,y1-rad),(x0,y0+rad)),ra(x0+rad,y0+rad,math.pi,3*math.pi/2)]
 for curve in holes:
  e=curve.toShape();p=[e.valueAt(t) for t in [e.FirstParameter,(e.FirstParameter+e.LastParameter)/2,e.LastParameter]]
  g['edges'].append({'type':'arc' if isinstance(e.Curve,Part.Circle) else 'line','points':[[v.x,v.y] for v in p]})
 hw=Part.Wire([c.toShape() for c in holes]);assert hw.isClosed();cutout=Part.Face(hw).extrude(V(0,0,3));cutout.translate(V(0,0,plan['board_bottom_global_z']-1));pcb=pcb.cut(cutout)
 g['cis_access_opening']=dict(bounds_mm=[x0,y0,x1,y1],corner_radius_mm=rad,clearance_mm=clear,reason='CIS connector underside intersects PCB raised by 1.6 mm',baseline_overlap_mm3=interference.Volume)
# KiCad drills the two RJ45 locating holes from its actual footprint. Match them
# in the CAD board; do not duplicate these as Edge.Cuts in KiCad.
placements=json.loads((here.parent.parents[1]/'Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/placements.json').read_text())
drills=[]
for pad in placements['J4']['pads']:
 dx,dy=pad['drill_mm']
 if dx>0:
  assert abs(dx-dy)<1e-8
  xk,yk=pad['xy_mm'];x,y=xk-50,68-yk
  tool=Part.makeCylinder(dx/2,3,V(x,y,plan['board_bottom_global_z']-1));pcb=pcb.cut(tool);drills.append(dict(x=x,y=y,diameter=dx))
g['footprint_drills']=drills
(out/'geometry.json').write_text(json.dumps(g,indent=2))
d=A.openDocument(str(out/'TouchBar_Montage_Photos.FCStd'))
for name,shape in [('PCB_Propose',pcb),('Coque_Reference',shell),('CIS_Reference',cis)]:
 o=d.addObject('Part::Feature',name);o.Shape=shape
oldpcb=source.Body025.Shape.copy();oldpcb.translate(V(0,0,-6));o=d.addObject('Part::Feature','PCB_Original');o.Shape=oldpcb
oldglass=source.Body023.Shape.copy();oldglass.translate(V(0,3.57,-9.4));o=d.addObject('Part::Feature','Ecran');o.Shape=oldglass
area=Part.makePlane(251,8.3,V(10.5,3.57+1.5,-9.405));o=d.addObject('Part::Feature','ZoneActive');o.Shape=area
checks={}
for key in ['Touch','Display']:
 for typ in ['Flex','Blindage','Connecteur']:
  s=d.getObject(key+'_'+typ).Shape
  checks[key+'_'+typ]={name:{'overlap_mm3':s.common(shape).Volume,'clearance_mm':s.distToShape(shape)[0]} for name,shape in [('coque',shell),('PCB_propose',pcb),('PCB_original',oldpcb),('CIS',cis)]}
# RJ45 is translated with the proposed PCB and included in contact checks.
rj=gs(source.TBV4_J4_Envelope);rj.translate(V(0,0,plan['pcb_raise_mm']));o=d.addObject('Part::Feature','RJ45');o.Shape=rj
for key in ['Touch','Display']:
 checks[key+'_RJ45_overlap_mm3']=sum(d.getObject(key+'_'+typ).Shape.common(rj).Volume for typ in ['Flex','Blindage','Connecteur'])
checks['RJ45_coque_overlap_mm3']=rj.common(shell).Volume
checks['PCB_CIS_overlap_mm3']=pcb.common(cis).Volume
checks['PCB_coque_overlap_mm3']=pcb.common(shell).Volume
checks['PCB_CIS_overlap_bounds']=str(pcb.common(cis).BoundBox)
checks['PCB_Original_CIS_overlap_mm3']=oldpcb.common(cis).Volume
checks['PCB_CIS_clearance_mm']=pcb.distToShape(cis)[0]
checks['PCB_area_mm2']=pcb.Volume
checks['PCB_valid']=pcb.isValid()
checks['PCB_solid_count']=len(pcb.Solids)
checks['CIS_opening']=g.get('cis_access_opening')
checks['ribbon_to_screen']={key+'_'+typ:d.getObject(key+'_'+typ).Shape.common(oldglass).Volume for key in ['Touch','Display'] for typ in ['Flex','Blindage','Connecteur']}
(out/'mechanical_checks.json').write_text(json.dumps(checks,indent=2));d.recompute();d.save();print(json.dumps(checks,indent=2))
