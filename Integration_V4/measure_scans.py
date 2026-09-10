"""Traceable scan survey. Pixel coordinates are hand-picked, not exact metrology.
Extract embedded JPEG without resampling; use the scan's 200 dpi, checked against
1 mm graph paper (~7.87 px/mm). Written measurements override optical estimates.
"""
import json,math
from pathlib import Path
here=Path(__file__).resolve().parent;src=here/'scans_2026-09-09'
scale=.127
# u: developed distance from flex departure; v: distance from upper long edge
# in front view with connectors at left. Both outlines use front-side scans.
touch_px=[[705,615.7480315],[749,615.7480315],[749,578],[759,565],[762,555],[762,453],[758,445],[731,440],[728,241],[750,239],[757,234],[757,208],[751,202],[700,202],[694,207],[694,440],[691,446],[689,455],[690,548],[694,562],[705,576]]
display_px=[[716,631.6220472],[779,631.6220472],[779,603],[782,587],[779,435],[751,423],[750,252],[745,246],[716,246],[709,251],[710,422],[712,432],[713,531],[713,585],[714,603]]
def transform(points,edge,right,departure):return [[round((edge-y)*scale+departure,6),round((right-x)*scale,6)] for x,y in points]
def rect(u0,v0,u1,v1):return [[u0,v0],[u1,v0],[u1,v1],[u0,v1]]
touch=dict(source='BRWCC5EF84396FF_000642.pdf',crosscheck='BRWCC5EF84396FF_000643.pdf',screen_edge_pixel_y=600,screen_upper_edge_pixel_x=771.5,departure_mm=2,outline_pixels=touch_px,outline_uv_mm=transform(touch_px,600,771.5,2),connector_center_uv_mm=[50.006,5.9055],connector_angle_flat_deg=90,connector_body_uv_size_mm=[2.4,6.6],head_rigid_interval_mm=[47.8,52.546],island_uv_bounds_mm=[5.3,1.2,21.9,10.5],metal_uv_bounds_mm=[11.65,1.2,21.685,10.477],metal_total_thickness_mm=1.15)
display=dict(source='BRWCC5EF84396FF_000645.pdf',crosscheck='BRWCC5EF84396FF_000644.pdf',screen_edge_pixel_y=608,screen_upper_edge_pixel_x=791.5,departure_mm=3,outline_pixels=display_px,outline_uv_mm=transform(display_px,608,791.5,3),connector_center_uv_mm=[43.45,8.0],connector_angle_flat_deg=0,connector_body_uv_size_mm=[8.55,1.7],head_rigid_interval_mm=[37.67,48.974],island_uv_bounds_mm=[5.2,1.2,26.1,10.0],metal_uv_bounds_mm=[5.667,1.2,12.271,10.0],metal_total_thickness_mm=1.5)
data=dict(revision='scans-2026-09-09',status='Releve nominal, non metrologique',mm_per_pixel=scale,nominal_dpi=200,estimated_edge_uncertainty_mm=.25,estimated_connector_position_uncertainty_mm=.5,departure_axis='Confirmation utilisateur 2026-09-10 : sortie horizontale sous ecran ; amorce de pli possible a 2/3 mm ou pres du bord',screen=dict(length_mm=262.7,width_mm=10.8,thickness_mm=1.5,active_insets_mm=dict(left=10.5,right=1.2,top=1.5,bottom=1.0),active_size_mm=[251,8.3]),flex_thickness_mm=.15,Touch=touch,Display=display)
(here/'measured_geometry.json').write_text(json.dumps(data,indent=2))
# Original images and trace overlays make every picked edge reviewable.
try:
 from PIL import Image
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 for key,g in [('Touch',touch),('Display',display)]:
  s=(src/g['source']).read_bytes();start=s.index(b'\xff\xd8');end=s.index(b'\xff\xd9',start)+2;jpg=src/(key+'_native.jpg');jpg.write_bytes(s[start:end]);im=Image.open(jpg)
  fig,ax=plt.subplots(figsize=(7,10));ax.imshow(im);pts=g['outline_pixels']+[g['outline_pixels'][0]];ax.plot([x[0] for x in pts],[x[1] for x in pts],color='#00aadd',linewidth=1)
  uc,vc=g['connector_center_uv_mm'];px=g['screen_upper_edge_pixel_x']-vc/scale;py=g['screen_edge_pixel_y']-(uc-g['departure_mm'])/scale;ax.plot(px,py,'+',color='red',markersize=14)
  ax.axhline(g['screen_edge_pixel_y'],color='#117744',linewidth=1);ax.set_xlim(min(p[0] for p in pts)-30,max(p[0] for p in pts)+30);ax.set_ylim(max(p[1] for p in pts)+20,min(p[1] for p in pts)-20)
  ax.set_title(key+' : contour releve et centre connecteur\n0,127 mm/pixel ; estimation ±0,5 mm sur centre',fontsize=11);ax.set_xlabel('pixel horizontal natif');ax.set_ylabel('pixel vertical natif');fig.tight_layout();fig.savefig(src/(key+'_releve.png'),dpi=160);plt.close(fig)
except ImportError:pass
print('Zone active 251 x 8.3 mm; flex 0.150 mm; measured scan outlines saved')
