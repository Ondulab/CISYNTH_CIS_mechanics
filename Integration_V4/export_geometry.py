import sys,json
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
m=Path(__file__).resolve().parent.parent;d=A.openDocument(str(m/'assemblage_v4.0.0.FCStd'))
s=d.Sketch085
edges=[]
for e in s.Shape.Edges:
 typ='arc' if isinstance(e.Curve,Part.Circle) else 'line'
 points=[e.valueAt(e.FirstParameter),e.valueAt((e.FirstParameter+e.LastParameter)/2),e.valueAt(e.LastParameter)]
 edges.append(dict(type=typ,points=[[v.x,v.y] for v in points]))
j={}
for ref,name,angle in [('J1','Sketch087',0),('J2','Sketch086',90)]:
 bb=d.getObject(name).Shape.BoundBox
 j[ref]=dict(sketch=name,center=[bb.Center.x,bb.Center.y],angle=angle,bounds=[bb.XMin,bb.YMin,bb.XMax,bb.YMax])
j['J4']=dict(center=[8.8265,9],angle=270,reason='Mouth toward negative X, at left end of board; shield land overhang is unresolved')
data=dict(source='assemblage_v4.0.0.FCStd',sketch='Sketch085',placement=[-23.9,-3.77,-6],size=[256,18,1],area=d.Body025.Shape.Volume,edges=edges,connectors=j,kicad_origin=[50,50],mapping='KiCad X=50+local X; KiCad Y=50+18-local Y; F.Cu=global Z -5 mm')
(m/'Integration_V4/geometry.json').write_text(json.dumps(data,indent=2))
print('edges',len(edges),'wires',len(s.Shape.Wires), 'closed',s.Shape.Wires[0].isClosed())
