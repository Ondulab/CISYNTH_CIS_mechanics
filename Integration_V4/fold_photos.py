"""Nominal mounting study using 10 September side photos.
Uses the scan polygons unchanged. Lateral registration remains a scan estimate.
Lengths and widths are conserved; bend radius is a mounting assumption, not a
manufacturer-qualified minimum. The previous scan study is retained separately.
"""
import json,math
from pathlib import Path
from fold_measured import A,Part,V,Route,surface_solid,make_shapes,unfolded_route,polyface,data,th,here
OUT=here/'Photos_2026-09-10';OUT.mkdir(exist_ok=True)
PARAMS=dict(board_bottom_global_z=-4.4,pcb_raise_mm=1.6,root_z_mm=-7.825,
    root_bend_radius_mm=.2,notch_bend_radius_mm=.2,
    root_bend_start_x_mm={'Touch':.3,'Display':3.0},
    folded_plane_z_mm={'Touch':-5.625,'Display':-7.275},
    lateral_registration_mm={'Touch':0.0,'Display':-.25},
    touch_return_start_x_mm=34.05,
    notch=dict(center_x=35.0,width=3.0,bottom_y=7.8))
class RegisteredRoute(Route):
 def __init__(self,*args,dy=0):super().__init__(*args);self.dy=dy
 def point(self,u,v,n=0):return super().point(u,v+self.dy,n)
def make_routes(params=PARAMS):
 routes={};meta={}
 for key in ['Touch','Display']:
  g=data[key];root=params['root_z_mm'];plane=params['folded_plane_z_mm'][key]
  r=RegisteredRoute(g['departure_mm'],root,math.pi,dy=params['lateral_registration_mm'][key]);R=params['root_bend_radius_mm']
  r.line(g['departure_mm']-params['root_bend_start_x_mm'][key])
  r.arc(R,-math.pi/2);r.line(plane-root-2*R);r.arc(R,-math.pi/2)
  root_end=r.u;headz=params['board_bottom_global_z']+1+(.7 if key=='Touch' else .6)+th/2;rise=headz-plane;R=params['notch_bend_radius_mm']
  if key=='Display':
   r.line(g['head_rigid_interval_mm'][0]-.3-r.u-rise-(math.pi-2)*R)
   r.arc(R,math.pi/2);axis=r.x;r.line(rise-2*R);r.arc(R,-math.pi/2)
  else:
   r.line(params['touch_return_start_x_mm']-r.x);r.arc(R,math.pi/2);axis=r.x;r.line(rise-2*R);r.arc(R,math.pi/2)
  bend_end=r.u;r.line(max(p[0] for p in g['outline_uv_mm'])-r.u)
  uc,vc=g['connector_center_uv_mm'];pt=r.point(uc,vc)
  routes[key]=r;meta[key]=dict(connector_xyz_mm=[pt.x,pt.y,params['board_bottom_global_z']+1],connector_rotation_deg=0 if key=='Display' else 270,root_end_u_mm=root_end,notch_axis_x_mm=axis,bend_end_u_mm=bend_end,developed_center_mm=uc,total_length_mm=r.u,lateral_registration_mm=r.dy,route=r.parts)
 return routes,meta
if __name__=='__main__':
 routes,meta=make_routes();d=A.newDocument('TouchBar_Photos_20260910');shapes={};checks={}
 for key in ['Touch','Display']:
  g=data[key];shapes[key]=make_shapes(routes[key],g)
  for typ,s in zip(['Flex','Blindage','Connecteur'],shapes[key]):
   o=d.addObject('Part::Feature',key+'_'+typ);o.Shape=s
   o.addProperty('App::PropertyString','Source');o.Source=g['source']+' + photos de profil 2026-09-10'
   o.addProperty('App::PropertyString','Statut');o.Statut='Montage nominal ; recalage scan et rayon de pli a confirmer sur piece'
   o.addProperty('App::PropertyLength','FlexThickness');o.FlexThickness=th
   o.addProperty('App::PropertyLength','BendRadius');o.BendRadius=PARAMS['notch_bend_radius_mm']
   o.addProperty('App::PropertyFloat','ScanLateralRegistration');o.ScanLateralRegistration=routes[key].dy
  flat=make_shapes(unfolded_route(g),g)
  for typ,s in zip(['Flex','Blindage','Connecteur'],flat):
   s=s.copy();s.translate(V(0,35 if key=='Touch' else 60,0));o=d.addObject('Part::Feature',key+'_Deplie_'+typ);o.Shape=s
  area=polyface([V(u,v,0) for u,v in g['outline_uv_mm']]).Area
  checks[key]=dict(valid=all(s.isValid() for s in shapes[key]),flex_solids=len(shapes[key][0].Solids),flat_flex_volume_mm3=area*th,folded_flex_volume_mm3=shapes[key][0].Volume,volume_relative_error=abs(shapes[key][0].Volume-area*th)/(area*th),rigid_head_bend_clearance_mm=g['head_rigid_interval_mm'][0]-meta[key]['bend_end_u_mm'])
 checks['between_ribbons']={a+'_'+b:dict(overlap_mm3=sa.common(sb).Volume,clearance_mm=sa.distToShape(sb)[0]) for a,sa in zip(['TouchFlex','TouchMetal','TouchPlug'],shapes['Touch']) for b,sb in zip(['DisplayFlex','DisplayMetal','DisplayPlug'],shapes['Display'])}
 plan=dict(PARAMS);plan.update(status='Montage nominal a verifier physiquement ; PCB sureleve de 1.6 mm',connectors=meta,checks=checks)
 (OUT/'fold_plan.json').write_text(json.dumps(plan,indent=2));d.recompute();d.saveAs(str(OUT/'TouchBar_Montage_Photos.FCStd'));print(json.dumps(checks,indent=2))
