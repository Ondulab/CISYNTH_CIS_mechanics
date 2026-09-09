"""Developable XZ folding of the scan-traced flexes, preserving their u length.
All dimensions mm. This generates a review proposal; adoption is separate.
"""
import sys,json,math
from pathlib import Path
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
here=Path(__file__).resolve().parent;data=json.loads((here/'measured_geometry.json').read_text())
V=A.Vector;th=data['flex_thickness_mm'];OFFSET_Y=3.57
class Route:
 def __init__(self,x,z,angle):self.x=x;self.z=z;self.angle=angle;self.u=0;self.parts=[]
 def line(self,length):
  assert length>=0
  self.parts.append(dict(kind='line',u0=self.u,u1=self.u+length,x=self.x,z=self.z,angle=self.angle))
  self.x+=length*math.cos(self.angle);self.z+=length*math.sin(self.angle);self.u+=length
 def arc(self,r,delta):
  sign=1 if delta>0 else -1;cx=self.x-sign*r*math.sin(self.angle);cz=self.z+sign*r*math.cos(self.angle)
  self.parts.append(dict(kind='arc',u0=self.u,u1=self.u+r*abs(delta),x=self.x,z=self.z,angle=self.angle,r=r,delta=delta,cx=cx,cz=cz))
  self.angle+=delta;self.x=cx+sign*r*math.sin(self.angle);self.z=cz-sign*r*math.cos(self.angle);self.u+=r*abs(delta)
 def pos(self,u):
  p=next((p for p in self.parts if p['u0']-1e-7<=u<=p['u1']+1e-7),self.parts[-1]);du=u-p['u0'];a=p['angle']
  if p['kind']=='line':return p['x']+du*math.cos(a),p['z']+du*math.sin(a),a
  sign=1 if p['delta']>0 else -1;a+=sign*du/p['r'];return p['cx']+sign*p['r']*math.sin(a),p['cz']-sign*p['r']*math.cos(a),a
 def point(self,u,v,n=0):
  x,z,a=self.pos(u);return V(x-n*math.sin(a),OFFSET_Y+v,z+n*math.cos(a))
def clip(poly,u,lower):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ina=a[0]>=u-1e-8 if lower else a[0]<=u+1e-8;inb=b[0]>=u-1e-8 if lower else b[0]<=u+1e-8
  if ina:out.append(a)
  if ina!=inb:
   t=(u-a[0])/(b[0]-a[0]);out.append([u,a[1]+t*(b[1]-a[1])])
 return out

def interval(poly,lo,hi):return clip(clip(poly,lo,True),hi,False)
def section_limits(poly,u):
 vals=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if abs(b[0]-a[0])<1e-8:
   if abs(a[0]-u)<1e-7:vals.extend([a[1],b[1]])
  elif min(a[0],b[0])-1e-7<=u<=max(a[0],b[0])+1e-7:
   t=(u-a[0])/(b[0]-a[0]);vals.append(a[1]+t*(b[1]-a[1]))
 assert vals,('no section',u)
 return min(vals),max(vals)
def polyface(points):
 clean=[]
 for p in points:
  if not clean or (p-clean[-1]).Length>1e-7:clean.append(p)
 if (clean[-1]-clean[0]).Length<1e-7:clean.pop()
 return Part.Face(Part.makePolygon(clean+[clean[0]]))
def surface_solid(route,poly,lo_n=-th/2,hi_n=th/2):
 solids=[]
 for p in route.parts:
  lo=max(p['u0'],min(q[0] for q in poly));hi=min(p['u1'],max(q[0] for q in poly))
  if hi-lo<1e-7:continue
  cropped=interval(poly,lo,hi)
  if len(cropped)<3:continue
  if p['kind']=='line':
   face=polyface([route.point(u,v,lo_n) for u,v in cropped]);a=p['angle'];solids.append(face.extrude(V(-(hi_n-lo_n)*math.sin(a),0,(hi_n-lo_n)*math.cos(a))))
  else:
   # The scan contour is constant-width in bend zones. Use exact annular surfaces.
   samples=[section_limits(poly,lo+(hi-lo)*t) for t in [.001,.25,.5,.75,.999]]
   if max(x[0] for x in samples)-min(x[0] for x in samples)<.015 and max(x[1] for x in samples)-min(x[1] for x in samples)<.015:
    v0,v1=samples[2];mid=(lo+hi)/2
    e=[Part.Arc(route.point(lo,v0,lo_n),route.point(mid,v0,lo_n),route.point(hi,v0,lo_n)).toShape(),Part.makeLine(route.point(hi,v0,lo_n),route.point(hi,v0,hi_n)),Part.Arc(route.point(hi,v0,hi_n),route.point(mid,v0,hi_n),route.point(lo,v0,hi_n)).toShape(),Part.makeLine(route.point(lo,v0,hi_n),route.point(lo,v0,lo_n))]
    solids.append(Part.Face(Part.Wire(e)).extrude(V(0,v1-v0,0)))
   else:
    # Ruled cross sections for a curved tapered root. No artificial XY stretching.
    steps=max(8,math.ceil((hi-lo)/.08));wires=[]
    for i in range(steps+1):
     u=lo+(hi-lo)*i/steps;v0,v1=section_limits(poly,u);pts=[route.point(u,v0,lo_n),route.point(u,v1,lo_n),route.point(u,v1,hi_n),route.point(u,v0,hi_n)];wires.append(Part.makePolygon(pts+[pts[0]]))
    solids.append(Part.makeLoft(wires,True,True))
 s=solids[0].multiFuse(solids[1:]).removeSplitter() if len(solids)>1 else solids[0]
 assert s.isValid(), 'invalid folded solid'
 return s

def make_routes(board_bottom=-4.4):
 # Metal islands face upward after the first half-turn; touch below display.
 # Front-view frame: x points from connector end towards screen, y downward.
 planes={'Touch':-7.275,'Display':-5.975};routes={};meta={}
 for key in ['Touch','Display']:
  g=data[key];root_z=-7.825 if key=='Touch' else -8.075
  r=Route(g['departure_mm'],root_z,math.pi);r.line(g['departure_mm']-1.4);r.arc((planes[key]-root_z)/2,-math.pi)
  if key=='Display':
   headz=board_bottom+1+.6+th/2;rise=headz-planes[key];radius=.45;bendlen=rise+(math.pi-2)*radius
   # Stop both bends before the scanned rigid connector head begins.
   end_u=g['head_rigid_interval_mm'][0]-.3
   r.line(end_u-r.u-bendlen);r.arc(radius,math.pi/2);r.line(rise-2*radius);r.arc(radius,-math.pi/2)
   meta[key]={'bend_end_u':r.u,'notch_axis_x':r.x-radius,'required_head_start_u':g['head_rigid_interval_mm'][0]}
  else:
   headz=board_bottom+1+.7+th/2;radius=(headz-planes[key])/2
   r.line(30.55-r.x);r.arc(radius,math.pi)
   meta[key]={'bend_end_u':r.u,'return_radius_mm':radius,'return_center_x':30.55}
  r.line(max(p[0] for p in g['outline_uv_mm'])-r.u)
  x,z,a=r.pos(g['connector_center_uv_mm'][0]);routes[key]=r;meta[key].update(connector_xyz_mm=[x,OFFSET_Y+g['connector_center_uv_mm'][1],board_bottom+1],connector_rotation_deg=0 if key=='Display' else 270,developed_center_mm=g['connector_center_uv_mm'][0],total_length_mm=r.u,route=r.parts)
 return routes,meta

def unfolded_route(g):
 r=Route(g['departure_mm'],-7.825,math.pi);r.line(max(p[0] for p in g['outline_uv_mm']));return r

def make_shapes(route,g):
 flex=surface_solid(route,g['outline_uv_mm']);u0,v0,u1,v1=g['island_uv_bounds_mm'];poly=interval(g['outline_uv_mm'],u0,u1)
 # Positive normal is the optical side before fold; first 180 flips metal upward.
 island=surface_solid(route,poly,th/2,g['metal_total_thickness_mm']-th/2)
 # Small terminal mate: dimensions belong to the real connector, not the large shield.
 uc,vc=g['connector_center_uv_mm'];du,dv=g['connector_body_uv_size_mm'];poly=[[uc-du/2,vc-dv/2],[uc+du/2,vc-dv/2],[uc+du/2,vc+dv/2],[uc-du/2,vc+dv/2]]
 # Scans: display mating face is opposite to touch before its additional 180 turn.
 plug=surface_solid(route,poly,(.075 if g is data['Touch'] else -.5),(.5 if g is data['Touch'] else -.075))
 return flex,island,plug

if __name__=='__main__':
 routes,meta=make_routes();d=A.newDocument('TouchBar_Scans_Proposition');shapes={};summary={}
 for key in ['Touch','Display']:
  g=data[key];shapes[key]=make_shapes(routes[key],g)
  for typ,shape in zip(['Flex','Blindage','Connecteur'],shapes[key]):
   o=d.addObject('Part::Feature',key+'_'+typ);o.Shape=shape;o.addProperty('App::PropertyString','Source');o.Source=g['source'];o.addProperty('App::PropertyString','Statut');o.Statut='Proposition, adaptation PCB en attente'
  flat=make_shapes(unfolded_route(g),g)
  for typ,shape in zip(['Flex','Blindage','Connecteur'],flat):
   shape=shape.copy();shape.translate(V(0,35 if key=='Touch' else 60,0));o=d.addObject('Part::Feature',key+'_Deplie_'+typ);o.Shape=shape
  outline=polyface([V(u,v,0) for u,v in g['outline_uv_mm']]);expected=outline.Area*th
  summary[key]={'valid':all(s.isValid() for s in shapes[key]),'flex_solids':len(shapes[key][0].Solids),'flat_flex_volume_mm3':expected,'folded_flex_volume_mm3':shapes[key][0].Volume,'volume_relative_error':abs(shapes[key][0].Volume-expected)/expected}
 summary['flex_and_island_overlap_mm3']=sum(a.common(b).Volume for a in shapes['Touch'][:2] for b in shapes['Display'][:2])
 (here/'fold_proposal.json').write_text(json.dumps(dict(board_bottom_global_z=-4.4,pcb_raise_mm=1.6,notch=dict(center_x=meta['Display']['notch_axis_x'],width=4.8,bottom_y=8.0),connectors=meta,checks=summary),indent=2))
 d.recompute();d.saveAs(str(here/'TouchBar_Scans_Proposition.FCStd'));print(json.dumps(summary,indent=2));print(json.dumps({k:{x:y for x,y in v.items() if x!='route'} for k,v in meta.items()},indent=2))
