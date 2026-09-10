"""Prepared only; run AFTER the concurrent task has finished editing.
FreeCAD bundled Python. Writes WHEC_CIS and, with --integrate, the current assembly.
"""
import sys, json, hashlib, shutil, datetime, math, os
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
from PySide2.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])
import FreeCAD as A, FreeCADGui as G, Part, Sketcher
G.showMainWindow()
ROOT = Path('/Users/zhonx/Documents/Workspaces/Workspace_Sp3ctra/Sp3ctra_CIS_Hardware/CIS/Meca/Sp3ctra_CIS_mechanics_v4')
OUT = ROOT / 'WHEC_CIS'
SOURCE = ROOT / 'assemblage_v4.0.0.FCStd'
V = A.Vector
PARAMS = [
 ('Length',232,'mm','WHEC p14','+/-0.5'), ('Width',18,'mm','WHEC p14','+/-0.3'),
 ('Height',11.7,'mm','WHEC p14','+/-0.3; glass face to rear frame'),
 ('MaxHeight',14,'mm','WHEC p14','maximum only'),
 ('GlassThickness',1.8,'mm','WHEC p14','no tolerance supplied'),
 ('HoleDiameter',2.2,'mm','WHEC p14','no tolerance supplied'),
 ('HoleDepth',6.5,'mm','WHEC p14','no tolerance supplied'),
 ('HoleEdge',1.8,'mm','WHEC p14','+/-0.2'),
 ('HolePitch',14.4,'mm','WHEC p14','+/-0.2'),
 ('HoleFromGlass',8.3,'mm','WHEC p14','+/-0.2'),
 ('ScanLength',216,'mm','WHEC p14','no tolerance supplied'),
 ('ScanEnd',8,'mm','WHEC p14','+/-0.5 from connector end'),
 ('ScanY',5.5,'mm','WHEC p14','+/-0.5'),
 ('FocusOffset',0.45,'mm','WHEC p14','no tolerance supplied; not material'),
 ('GlassBevel',0.4,'mm','WHEC p14','+/-0.15; all-edge application provisional'),
 ('GlassBevelAngle',45,'deg','WHEC p14','+/-5'),
 ('GlassInset',0,'mm','ASSUMPTION','glass plan uses full outer envelope; actual insets unknown'),
 ('EndWall',7.5,'mm','ASSUMPTION','internal end wall allows blind holes'),
 ('SideWall',1,'mm','ASSUMPTION','internal wall unknown'),
 ('RearRecess',1.3,'mm','LEGACY / ASSUMPTION','rear PCB recess unknown'),
 ('PCBInset',1.1,'mm','LEGACY / ASSUMPTION','PCB perimeter unknown'),
 ('PCBThickness',1,'mm','LEGACY / ASSUMPTION','PCB thickness unknown'),
 ('PCBRearZ',0,'mm','LEGACY / ASSUMPTION','PCB flush rear hypothesis'),
 ('ConnectorWidth',14.9,'mm','JST FLZ family p3','specific GAN/equivalent unverified'),
 ('ConnectorDepth',4.6,'mm','JST FLZ family p3','closed body, excludes rear contact extension'),
 ('ConnectorHeight',2,'mm','JST FLZ family p3','specific GAN/equivalent unverified'),
 ('ConnectorTail',0.7,'mm','JST FLZ family p3','reference dimension; envelope only'),
 ('ConnectorX',208,'mm','GRAPHICAL ESTIMATE','center from WHEC drawing; no manufacturer location dimension'),
 ('ConnectorY',11.7,'mm','GRAPHICAL ESTIMATE','center and side interpretation require physical confirmation'),
]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def expr(o,p,e): o.setExpression(p,'WHEC_Parameters.'+e if e.isidentifier() else e)
def E(s):
 import re
 return re.sub(r'\b[A-Za-z][A-Za-z0-9]*\b',lambda m: 'WHEC_Parameters.'+m[0] if m[0] in {r[0] for r in PARAMS} else m[0],s)
def note(o,text):
 o.addProperty('App::PropertyString','DimensionStatus','WHEC');o.DimensionStatus=text

def rectangle(d,body,name,label,w,h,xyz,rotation=None):
 s=d.addObject('Sketcher::SketchObject','WHEC_'+name);body.addObject(s);s.Label=label
 s.Placement=A.Placement(V(*xyz),rotation or A.Rotation())
 pts=[(0,0),(w,0),(w,h),(0,h)]
 for i in range(4):
  a,b=pts[i],pts[(i+1)%4];s.addGeometry(Part.LineSegment(V(*a,0),V(*b,0)),False)
 for i in range(4):s.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%4,1))
 for i in [0,2]:s.addConstraint(Sketcher.Constraint('Horizontal',i))
 for i in [1,3]:s.addConstraint(Sketcher.Constraint('Vertical',i))
 s.addConstraint(Sketcher.Constraint('Coincident',0,1,-1,1))
 ci=s.addConstraint(Sketcher.Constraint('Distance',0,w));s.renameConstraint(ci,'Dimension1')
 cj=s.addConstraint(Sketcher.Constraint('Distance',1,h));s.renameConstraint(cj,'Dimension2')
 return s

def rectexpr(s,w,h,xyz):
 s.setExpression('Constraints.Dimension1',E(w));s.setExpression('Constraints.Dimension2',E(h))
 for axis,v in zip('xyz',xyz):
  if v is not None:s.setExpression('Placement.Base.'+axis,E(v))

def feature(d,b,name,typ,s,length,length_expr):
 o=b.newObject('PartDesign::'+typ,'WHEC_'+name);o.Profile=s;o.Length=length
 o.setExpression('Length',E(length_expr));d.recompute();s.Visibility=False
 for q in b.Group:
  if q!=o:q.Visibility=False
 return o

def build(d,group):
 sheet=d.addObject('Spreadsheet::Sheet','WHEC_Parameters');sheet.Label='WHEC — cotes constructeur et hypothèses';group.addObject(sheet)
 for c,t in zip('ABCDE',['Parameter','Nominal','Unit','Source / certainty','Tolerance / interpretation']):sheet.set(c+'1',t)
 for row,(key,value,unit,source,info) in enumerate(PARAMS,2):
  for col,val in zip('ABCDE',[key,str(value)+' '+unit,unit,source,info]):sheet.set(col+str(row),val)
  sheet.setAlias('B'+str(row),key)
  if 'ASSUMPTION' in source or 'ESTIMATE' in source:sheet.setBackground('A'+str(row)+':E'+str(row),(1,.87,.64))
 sheet.setColumnWidth('A',180);sheet.setColumnWidth('B',95);sheet.setColumnWidth('D',230);sheet.setColumnWidth('E',440)
 note(group,'LC3R216N-8008; HHIK-8008A Preliminary 2023-12-18. See WHEC_CIS/RELEVE_COTES.md and MODELISATION.md. Nominal external dimensions; internal geometry provisional.')
 d.recompute()
 b=d.addObject('PartDesign::Body','WHEC_Housing');group.addObject(b);b.Label='WHEC — cadre / intérieur provisoire'
 s=rectangle(d,b,'FrameProfile','Cadre — 232 × 18',232,18,(0,0,0));rectexpr(s,'Length','Width',(None,None,None))
 feature(d,b,'FramePad','Pad',s,9.9,'Height-GlassThickness')
 s=rectangle(d,b,'OpticalCavity','Cavité interne — hypothèse',217,16,(7.5,1,9.9));rectexpr(s,'Length-2*EndWall','Width-2*SideWall',('EndWall','SideWall','Height-GlassThickness'))
 feature(d,b,'OpticalPocket','Pocket',s,8.6,'Height-GlassThickness-RearRecess')
 s=rectangle(d,b,'RearSeat','Logement PCB — hypothèse',229.8,15.8,(1.1,1.1,0));rectexpr(s,'Length-2*PCBInset','Width-2*PCBInset',('PCBInset','PCBInset',None))
 rear=feature(d,b,'RearPocket','Pocket',s,1.3,'RearRecess');rear.Reversed=True;d.recompute()
 # Local sketch u=Y, v=Z, normal +X. Pockets enter each end separately.
 rot=A.Rotation(V(0,1,0),V(0,0,1),V(1,0,0),'ZXY')
 for side,x,rev in [('Left',0,True),('Right',232,False)]:
  sk=d.addObject('Sketcher::SketchObject','WHEC_Holes'+side);b.addObject(sk);sk.Label='Fixations '+side+' — Ø2,2 × 6,5 borgnes'
  sk.Placement=A.Placement(V(x,0,0),rot)
  if side=='Right':sk.setExpression('Placement.Base.x',E('Length'))
  for i,y in enumerate([1.8,16.2]):
   sk.addGeometry(Part.Circle(V(y,3.4,0),V(0,0,1),1.1),False)
   for typ,val,key,formula in [('DistanceX',y,'Y'+str(i),'HoleEdge'+('' if i==0 else '+HolePitch')),('DistanceY',3.4,'Z'+str(i),'Height-HoleFromGlass')]:
    c=sk.addConstraint(Sketcher.Constraint(typ,i,3,val));sk.renameConstraint(c,key);sk.setExpression('Constraints.'+key,E(formula))
   c=sk.addConstraint(Sketcher.Constraint('Diameter',i,2.2));sk.renameConstraint(c,'D'+str(i));sk.setExpression('Constraints.D'+str(i),E('HoleDiameter'))
  o=feature(d,b,'HolesPocket'+side,'Pocket',sk,6.5,'HoleDepth');o.Reversed=rev;d.recompute()
 b.Tip.ViewObject.ShapeColor=(.10,.11,.12);b.ViewObject.ShapeColor=(.10,.11,.12)
 note(b,'Outer envelope and holes: WHEC. Internal cavity, wall and rear seat dimensions: provisional.')
 glass=d.addObject('PartDesign::Body','WHEC_Glass');group.addObject(glass);glass.Label='WHEC — vitre 1,8 / pourtour provisoire'
 s=rectangle(d,glass,'GlassProfile','Vitre — longueur/largeur enveloppes supposées',232,18,(0,0,9.9));rectexpr(s,'Length-2*GlassInset','Width-2*GlassInset',('GlassInset','GlassInset','Height-GlassThickness'))
 pad=feature(d,glass,'GlassPad','Pad',s,1.8,'GlassThickness')
 edges=['Edge'+str(i+1) for i,e in enumerate(pad.Shape.Edges) if abs(e.BoundBox.ZMin-11.7)<1e-6 and abs(e.BoundBox.ZMax-11.7)<1e-6]
 chamfer=glass.newObject('PartDesign::Chamfer','WHEC_GlassChamfer');chamfer.Base=(pad,edges);chamfer.Size=.4;chamfer.setExpression('Size',E('GlassBevel'));d.recompute();pad.Visibility=False
 # Equal-distance chamfer represents the documented nominal 45 degrees.
 glass.ViewObject.ShapeColor=(.66,.82,.86);chamfer.ViewObject.ShapeColor=(.66,.82,.86);chamfer.ViewObject.Transparency=65
 note(glass,'1.8 thickness confirmed, tolerance unknown. Plan dimensions use maximum frame envelope provisionally. Bevel applied to all four top edges provisionally; 45-degree nominal.')
 pcb=d.addObject('PartDesign::Body','WHEC_PCB');group.addObject(pcb);pcb.Label='WHEC — PCB interne / dimensions provisoires'
 s=rectangle(d,pcb,'PCBProfile','PCB — contour provisoire',229.8,15.8,(1.1,1.1,0));rectexpr(s,'Length-2*PCBInset','Width-2*PCBInset',('PCBInset','PCBInset','PCBRearZ'))
 o=feature(d,pcb,'PCBPad','Pad',s,1,'PCBThickness');o.ViewObject.ShapeColor=(.08,.30,.14);pcb.ViewObject.ShapeColor=(.08,.30,.14)
 note(pcb,'All PCB dimensions and rear Z position are unconfirmed for WHEC; inherited values adjusted with overall length.')
 conn=d.addObject('PartDesign::Body','WHEC_Connector');group.addObject(conn);conn.Label='WHEC — FFC 18 contacts / enveloppe et position provisoires'
 s=rectangle(d,conn,'ConnectorProfile','FLZ 18 — enveloppe fermée, contacts inclus',14.9,5.3,(200.55,9.05,-2));rectexpr(s,'ConnectorWidth','ConnectorDepth+ConnectorTail',('ConnectorX-ConnectorWidth/2','ConnectorY-(ConnectorDepth+ConnectorTail)/2','PCBRearZ-ConnectorHeight'))
 o=feature(d,conn,'ConnectorPad','Pad',s,2,'ConnectorHeight');o.ViewObject.ShapeColor=(.89,.88,.75);conn.ViewObject.ShapeColor=(.89,.88,.75)
 note(conn,'Simplified JST FLZ family bounding envelope only. X=208,Y=11.7 are drawing estimates, Z follows assumed PCB. No pin/slider detail certification.')
 sk=d.addObject('Sketcher::SketchObject','WHEC_ReadingLine');group.addObject(sk);sk.Label='Repère optique — 216 mm / 0,45 au-dessus du verre'
 sk.Placement.Base=V(0,0,12.15);sk.setExpression('Placement.Base.z',E('Height+FocusOffset'))
 sk.addGeometry(Part.LineSegment(V(8,5.5,0),V(224,5.5,0)),False)
 for c,key,f in [(Sketcher.Constraint('DistanceX',0,1,8),'StartX','Length-ScanEnd-ScanLength'),(Sketcher.Constraint('DistanceY',0,1,5.5),'LineY','ScanY'),(Sketcher.Constraint('Distance',0,216),'UsefulLength','ScanLength')]:
  i=sk.addConstraint(c);sk.renameConstraint(i,key);sk.setExpression('Constraints.'+key,E(f))
 sk.addConstraint(Sketcher.Constraint('Horizontal',0));sk.ViewObject.LineColor=(1,.25,.05);sk.ViewObject.LineWidth=3
 note(sk,'Optical datum only, not physical material. Start of useful scanning is at high X (pixel 41 in 600 dpi).')
 d.recompute()
 return [b,glass,pcb,conn]

if __name__=='__main__':
 raise SystemExit('Preparation only: release gate and final verification driver must be added after the other instance finishes.')
