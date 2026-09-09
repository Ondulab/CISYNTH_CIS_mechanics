"""Export the same provisional connector envelopes to KiCad's footprint frames."""
import sys,json
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
here=Path(__file__).resolve().parent;m=here.parent
out=m.parents[1]/'Electronique/Sp3ctra_CIS_electronics_v4/Integration_Mecanique/models';out.mkdir(exist_ok=True)
g=json.loads((here/'geometry.json').read_text());d=A.openDocument(str(m/'assemblage_v4.0.0.FCStd'))
for ref,name in [('J1','TBV4_J1_Socket'),('J2','TBV4_J2_Socket'),('J4','TBV4_J4_Envelope')]:
 o=d.getObject(name);s=o.Shape.copy();s.Placement=o.getGlobalPlacement();x,y=g['connectors'][ref]['center'];s.translate(A.Vector(23.9-x,3.77-y,5));s.rotate(A.Vector(),A.Vector(0,0,1),-g['connectors'][ref]['angle']);s.exportStep(str(out/(ref+'_envelope.step')))
print('3 connector envelopes exported')
