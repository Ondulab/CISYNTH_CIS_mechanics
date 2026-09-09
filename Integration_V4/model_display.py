"""LEGACY FLEX GENERATOR: superseded by fold_measured.py for scan-derived flexes.
FreeCAD Python: regenerate provisional Touch Bar envelopes in existing assembly.
Coordinates below are PCB-local XY, Z from the bottom PCB face. Dimensions not
measured on the original flex are explicitly provisional. No hidden bend-radius claim.
"""
import sys, json, math
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
from PySide2.QtWidgets import QApplication
app=QApplication.instance() or QApplication([])
import FreeCAD as A, Part, FreeCADGui as G
G.showMainWindow()
here=Path(__file__).resolve().parent;m=here.parent
d=A.openDocument(str(m/'assemblage_v4.0.0.FCStd'))
geo=json.loads((here/'geometry.json').read_text())
P=A.Vector
def V(x,y,z):return P(x-23.9,y-3.77,z-6)
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
# Only remove our generated objects on a repeat run.
for o in list(d.Objects):
 if o.Name.startswith('TBV4_'):d.removeObject(o.Name)
parts=[]
def feature(parent,name,label,shape,color,provisional=True):
 o=d.addObject('PartDesign::Feature' if parent.TypeId=='PartDesign::Body' else 'Part::Feature','TBV4_'+name)
 parent.addObject(o)
 # Shape is global; store geometry relative to the actual parent.
 shape=shape.copy();shape.transformShape(parent.getGlobalPlacement().inverse().toMatrix())
 o.Shape=shape;o.Label=label
 o.addProperty('App::PropertyString','Validation','Integration');o.Validation='Enveloppe provisoire a mesurer sur la piece' if provisional else 'Extrait de la geometrie source'
 o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.12,.12,.12);o.ViewObject.DisplayMode='Flat Lines';parts.append(o);return o
# Optical zone: square-pixel ratio from RE; actual active width remains unmeasured.
active_length=251.0;active_height=8.3
opt=Part.makePlane(active_length,active_height,P(-23.9+10.5,-.2+1.5,-9.405))
a=feature(d.Part025,'ActiveArea','Zone OLED — dimensions mesurees 251 x 8,3 mm',opt,(.045,.23,.31))
for name,val in [('LongueurActive',active_length),('HauteurActive',active_height)]:a.addProperty('App::PropertyLength',name,'Dimensions');setattr(a,name,val)
d.Body023.ViewObject.ShapeColor=(.025,.025,.03);d.Pad019.ViewObject.ShapeColor=(.025,.025,.03)
# Ribbon primitives: planar strips and circular bends with real finite thickness.
th=.12

def strip(points,y,w):
 # points are X,Z; constant width along Y; open spine gets a rectangular sweep.
 pts=[V(x,y-w/2,z) for x,z in points]
 spine=Part.Wire([Part.makeLine(a,b) for a,b in zip(pts,pts[1:])])
 dx=points[1][0]-points[0][0];dz=points[1][1]-points[0][1];length=math.hypot(dx,dz);nx=-dz/length*th/2;nz=dx/length*th/2
 x,z=points[0];p=[V(x+nx,y-w/2,z+nz),V(x+nx,y+w/2,z+nz),V(x-nx,y+w/2,z-nz),V(x-nx,y-w/2,z-nz)];p.append(p[0])
 return spine.makePipeShell([Part.Wire(Part.makePolygon(p).Edges)],True,False)
def bend(cx,cz,r,a0,a1,y,w):
 def v(rad,deg):t=math.radians(deg);return V(cx+rad*math.cos(t),y-w/2,cz+rad*math.sin(t))
 ro=r+th/2;ri=r-th/2;mid=(a0+a1)/2
 e=[Part.Arc(v(ro,a0),v(ro,mid),v(ro,a1)).toShape(),Part.makeLine(v(ro,a1),v(ri,a1)),Part.Arc(v(ri,a1),v(ri,mid),v(ri,a0)).toShape(),Part.makeLine(v(ri,a0),v(ro,a0))]
 return Part.Face(Part.Wire(e)).extrude(P(0,w,0))
def flat(x0,y0,x1,y1,w,z):
 # Constant lateral width; transitions remain planar, cut outline is provisional.
 v=[V(x0,y0-w/2,z-th/2),V(x1,y1-w/2,z-th/2),V(x1,y1+w/2,z-th/2),V(x0,y0+w/2,z-th/2)];v.append(v[0]);return Part.Face(Part.makePolygon(v)).extrude(P(0,0,th))
def union(seq):
 s=seq[0].multiFuse(seq[1:]).removeSplitter();assert s.isValid();return s
cx,cy=geo['connectors']['J1']['center'];tx,ty=geo['connectors']['J2']['center']
mipi=union([strip([(1.4,-1.9),(1.4,-1.15)],12.2,2.6),bend(1.85,-1.15,.45,180,90,12.2,2.6),flat(1.85,12.2,5,12.2,2.6,-.7),flat(5,12.2,9,11.5,2.6,-.7),flat(9,11.5,26.5,11.5,2.6,-.7),flat(26.5,11.5,30.5,15,2.6,-.7),flat(30.5,15,34.95,15,2.6,-.7),bend(34.95,-.25,.45,-90,0,15,2.6),strip([(35.4,-.25),(35.4,1.21)],15,2.6),bend(35.85,1.21,.45,180,90,15,2.6),flat(35.85,15,38.5,15,2.6,1.66),flat(38.5,15,cx,cy,2.6,1.66),box(cx-4.45,cy-1.3,1.6,8.9,2.6,th)])
touch=union([strip([(1.4,-1.9),(1.4,-1.35)],7,2.4),bend(1.8,-1.35,.4,180,90,7,2.4),flat(1.8,7,5,7,2.4,-.95),flat(5,7,9,11.25,2.4,-.95),flat(9,11.25,34.5,11.25,2.4,-.95),bend(34.5,.405,1.355,-90,90,11.25,2.4),flat(34.5,11.25,tx,ty,2.4,1.76),box(tx-1.9,ty-3.6,1.7,3.8,7.2,th)])
f1=feature(d.Part025,'MIPI_Flex','Nappe MIPI — passage encoche PCB',mipi,(.74,.39,.08));f2=feature(d.Part025,'Touch_Flex','Nappe tactile — retour 180°',touch,(.9,.57,.12))
for f,w in [(f1,2.6),(f2,2.4)]:
 f.addProperty('App::PropertyLength','Epaisseur','Dimensions');f.Epaisseur=th;f.addProperty('App::PropertyLength','LargeurPassage','Dimensions');f.LargeurPassage=w
# Receptacle and mating plug envelopes; mating faces point toward one another.
for ref,x,y,dx,dy,h in [('J1',cx,cy,8.55,1.7,.6),('J2',tx,ty,3.8,7.2,.7)]:
 socket=box(x-dx/2,y-dy/2,1,dx,dy,h-.12)
 # Open centre gives a recognisable receptacle, male tongue enters from above.
 socket=socket.cut(box(x-dx/2+.22,y-dy/2+.22,1.16,dx-.44,dy-.44,h))
 so=feature(d.Part008,ref+'_Socket',ref+' — embase PCB '+('BM28B0.6-34DS' if ref=='J1' else 'AA07-S022VA1 MOCKUP'),socket,(.14,.15,.16))
 plug=box(x-dx/2+.22,y-dy/2+.22,1.16,dx-.44,dy-.44,h-.16)
 feature(d.Part025,ref+'_Plug',ref+' — connecteur nappe '+('BM28B0.6-34DP, enveloppe' if ref=='J1' else 'tactile, enveloppe provisoire'),plug,(.22,.22,.24))
 # Reproduce actual pad XY/pin numbering from KiCad, giving traceable orientation.
 placements=json.loads((m.parents[1]/'Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/placements.json').read_text())
 pins=[]
 for p in placements[ref]['pads']:
  xk,yk=p['xy_mm'];sx,sy=p['size_mm'];xp=xk-50;yp=68-yk
  if ref=='J2':sx,sy=sy,sx
  pins.append(box(xp-sx/2,yp-sy/2,1,sx,sy,.025))
 feature(d.Part008,ref+'_Pads',ref+' — plages PCB / orientation KiCad',Part.makeCompound(pins),(.88,.72,.22),False)
# RJ45 external envelope from current Würth drawing, placed using footprint origin.
# Footprint front edge = local Y +8.8265, global mouth X = PCB-local 0.
x0=0;y0=9-16.4/2
outer=box(x0,y0,1,15.7,16.4,13.4)
opening=box(x0-.01,9-6,2.1,12,12,8.5)
rj=outer.cut(opening)
feature(d.Part008,'J4_Envelope','J4 — Wurth 634008137521, enveloppe',rj,(.66,.69,.72))
# Report exact intersections, without concealing pre-existing design conflicts.
def globalshape(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
shell=globalshape(d.Body022);pcb=globalshape(d.Body025);cis=globalshape(d.Body)
report={}
for name,s in [('MIPI',mipi),('Touch',touch),('J4',rj)]:
 report[name]={'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'shell_overlap_mm3':s.common(shell).Volume,'pcb_overlap_mm3':s.common(pcb).Volume,'cis_overlap_mm3':s.common(cis).Volume}
report['flex_mutual_overlap_mm3']=mipi.common(touch).Volume
report['parameters_provisional']={'flex_thickness':th,'mipi_width':2.6,'touch_width':2.4,'active_length':active_length,'active_height':active_height,'touch_radius':1.355,'mipi_radius':.45}
(here/'mechanical_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
d.recompute()
# Keep user-created placement sketches and their geometry intact; hide their display.
d.Sketch086.Visibility=False;d.Sketch087.Visibility=False
for o in parts:o.Visibility=True
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
d.save()
# Standalone review assembly: source shapes + additions only, no construction history.
review=A.newDocument('Integration_TouchBar_V4')
for original in [d.Body022,d.Body025,d.Body023]+parts:
 o=review.addObject('Part::Feature',original.Name);o.Label=original.Label;o.Shape=globalshape(original);o.ViewObject.ShapeColor=original.ViewObject.ShapeColor
 if original==d.Body022:o.ViewObject.Transparency=85
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();review.recompute();review.saveAs(str(here/'Integration_TouchBar_V4.FCStd'))
# Neutral review export includes the actual PCB, display and all generated geometry.
Part.export([o for o in review.Objects if hasattr(o,'Shape')],str(here/'Integration_TouchBar_V4.step'))
