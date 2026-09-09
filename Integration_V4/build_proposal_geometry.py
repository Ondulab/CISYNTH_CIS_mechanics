import sys,json,math
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
here=Path(__file__).resolve().parent;source=A.openDocument(str(here.parent/'assemblage_v4.0.0.FCStd'));plan=json.loads((here/'fold_proposal.json').read_text());g=json.loads((here/'geometry.json').read_text())
c=plan['notch']['center_x'];L=c-plan['notch']['width']/2;R=c+plan['notch']['width']/2;y=plan['notch']['bottom_y'];V=A.Vector
def seg(a,b):return Part.LineSegment(V(a[0],a[1],0),V(b[0],b[1],0))
def arc(x,y,a,b):return Part.ArcOfCircle(Part.Circle(V(x,y,0),V(0,0,1),1),a,b)
replacements={2:seg((255,18),(R+1,18)),34:seg((L,17),(L,y+1)),35:seg((L+1,y),(R-1,y)),36:seg((L-1,18),(26.4,18)),37:seg((R,y+1),(R,17)),38:arc(L-1,17,0,math.pi/2),40:arc(R+1,17,math.pi/2,math.pi),42:arc(L+1,y+1,math.pi,3*math.pi/2),44:arc(R-1,y+1,3*math.pi/2,2*math.pi)}
edges=[];geoms=[]
for i,orig in enumerate(source.Sketch085.Geometry):
 curve=replacements.get(i,orig)
 if isinstance(curve,Part.Point):continue
 e=curve.toShape();geoms.append(curve);p=[e.valueAt(t) for t in [e.FirstParameter,(e.FirstParameter+e.LastParameter)/2,e.LastParameter]];edges.append({'type':'arc' if isinstance(e.Curve,Part.Circle) else 'line','points':[[v.x,v.y] for v in p]})
g['edges']=edges;g['placement'][2]=plan['board_bottom_global_z'];g['status']='PROPOSITION : adaptation hauteur et encoche en attente';g['notch']=plan['notch']
for ref,key in [('J1','Display'),('J2','Touch')]:
 g['connectors'][ref]['center']=plan['connectors'][key]['connector_xyz_mm'][:2];g['connectors'][ref]['angle']=plan['connectors'][key]['connector_rotation_deg'];g['connectors'][ref]['source']='scan + conservation longueur developpee';g['connectors'][ref]['former_sketch_center']=json.loads((here/'geometry.json').read_text())['connectors'][ref]['center']
g['mapping']='X=50+Xlocal; Y=68-Ylocal; F.Cu=Zglobal '+str(plan['board_bottom_global_z']+1)
(here/'geometry_proposal.json').write_text(json.dumps(g,indent=2))
w=Part.Wire(Part.__sortEdges__([c.toShape() for c in geoms]));assert w.isClosed();pcb=Part.Face(w).extrude(V(0,0,1));pcb.translate(V(0,0,plan['board_bottom_global_z']))
def gs(o):s=o.Shape.copy();s.Placement=o.getGlobalPlacement();s.translate(V(23.9,3.77,0));return s
shell=gs(source.Body022);cis=gs(source.Body)
d=A.openDocument(str(here/'TouchBar_Scans_Proposition.FCStd'))
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
(here/'proposal_checks.json').write_text(json.dumps(checks,indent=2));d.recompute();d.save();print(json.dumps(checks,indent=2))
