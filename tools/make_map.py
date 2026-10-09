import json, math, random
random.seed(7)
d=json.load(open('research/ne_admin0.json'))
jp=[f for f in d['features'] if f['properties'].get('ADM0_A3')=='JPN'][0]['geometry']
polys=jp['coordinates'] if jp['type']=='MultiPolygon' else [jp['coordinates']]
LON0,LAT0,S=128.8,46.0,47.0
C=math.cos(math.radians(37.5))
def P(lon,lat): return ((lon-LON0)*C*S,(LAT0-lat)*S)
W,H=665,760
rings=[]
for poly in polys:
    ring=poly[0]
    xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
    if max(xs)<129.3 or min(ys)<30.6 and max(ys)<32: pass
    if max(ys)<30.9 or min(xs)>146.5 or max(xs)<129.0: continue
    area=(max(xs)-min(xs))*(max(ys)-min(ys))
    if area<0.25: continue
    rings.append(ring)
def simplify(pts,t=0.35):
    out=[pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0]-out[-1][0],p[1]-out[-1][1])>=t: out.append(p)
    return out
land=''
prj=[]
for r in rings:
    pp=simplify([P(*p) for p in r])
    prj.append(pp)
    land+='M'+'L'.join(f'{x:.1f} {y:.1f}' for x,y in pp)+'Z'
def inside(x,y,pp):
    c=False;j=len(pp)-1
    for i in range(len(pp)):
        xi,yi=pp[i];xj,yj=pp[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: c=not c
        j=i
    return c
def mask(x,y): return any(inside(x,y,pp) for pp in prj)
ridges=[ # lon,lat points, height, sigma(km-ish in lat deg)
 ([(137.62,36.58),(137.65,36.34),(137.65,36.2),(137.68,36.0),(137.8,35.78)],1.0,0.22),   # northern alps
 ([(138.25,35.85),(138.2,35.6),(138.2,35.35),(138.15,35.2)],0.95,0.2),                      # southern alps
 ([(137.85,35.9),(137.9,35.6),(137.8,35.45)],0.7,0.2),                                       # central alps
 ([(138.73,35.36)],1.0,0.17),                                                               # fuji
 ([(138.9,36.83),(139.1,36.85),(138.6,36.6),(138.5,36.4)],0.7,0.22),                         # joshinetsu
 ([(139.7,37.1),(140.1,37.6),(140.5,38.2),(140.7,39.0),(141.0,39.9),(140.9,40.6)],0.55,0.28), # tohoku
 ([(142.85,43.65),(142.5,43.3),(143.0,43.0),(144.2,43.6)],0.7,0.35),                         # daisetsu
 ([(142.7,42.8),(143.0,42.5),(143.3,42.7)],0.5,0.25),
 ([(135.9,34.1),(136.1,34.4),(135.7,34.0)],0.35,0.2),                                        # kii
 ([(133.3,33.8),(133.0,33.8),(134.0,33.9)],0.4,0.2),                                         # shikoku
 ([(131.0,32.9),(131.3,32.8)],0.4,0.25),                                                     # kyushu
 ([(136.3,35.5),(136.0,35.4)],0.3,0.2),
]
def dseg(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay
    L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.hypot(px-ax-t*dx,py-ay-t*dy)
def field(lon,lat):
    m=0
    for pts,h,s in ridges:
        dm=min(dseg(lon,lat,pts[i],pts[i+1]) for i in range(len(pts)-1)) if len(pts)>1 else math.hypot(lon-pts[0][0],lat-pts[0][1])
        m=max(m,h*math.exp(-(dm/s)**2))
    m+=0.045*math.sin(lon*7.1+lat*3.3)+0.035*math.sin(lon*13.7-lat*9.1)+0.02*math.sin(lon*29+lat*23)
    return m
# grid in projected space
step=4.0
nx,ny=int(W/step)+1,int(H/step)+1
g=[[0.0]*nx for _ in range(ny)]
for j in range(ny):
    for i in range(nx):
        x,y=i*step,j*step
        lon=LON0+x/(C*S); lat=LAT0-y/S
        g[j][i]=field(lon,lat) if mask(x,y) else -0.2
levels=[0.12,0.22,0.32,0.42,0.52,0.62,0.72,0.82,0.92]
def lerp(a,b,v): return (v-a)/(b-a) if b!=a else 0.5
out={}
for li,lv in enumerate(levels):
    segs=[]
    for j in range(ny-1):
        for i in range(nx-1):
            v=[g[j][i],g[j][i+1],g[j+1][i+1],g[j+1][i]]
            idx=sum((1<<k) for k in range(4) if v[k]>=lv)
            if idx in(0,15): continue
            x0,y0=i*step,j*step
            e={0:(x0+lerp(v[0],v[1],lv)*step,y0),1:(x0+step,y0+lerp(v[1],v[2],lv)*step),
               2:(x0+lerp(v[3],v[2],lv)*step,y0+step),3:(x0,y0+lerp(v[0],v[3],lv)*step)}
            tbl={1:[(3,0)],2:[(0,1)],3:[(3,1)],4:[(1,2)],5:[(3,0),(1,2)],6:[(0,2)],7:[(3,2)],8:[(2,3)],9:[(0,2)],10:[(0,1),(2,3)],11:[(1,2)],12:[(1,3)],13:[(0,1)],14:[(3,0)]}
            for a,b in tbl[idx]:
                segs.append((e[a],e[b]))
    out[li]=''.join(f'M{a[0]:.0f} {a[1]:.0f}L{b[0]:.0f} {b[1]:.0f}' for a,b in segs)
M={ 'fuji':(138.7274,35.3606),'hotaka':(137.6478,36.2893),'yari':(137.6476,36.3419),'tate':(137.6178,36.5774),'tanigawa':(138.9293,36.8344)}
pos={k:[round(v,1) for v in P(*c)] for k,c in M.items()}
js='window.MAPDATA='+json.dumps({'w':W,'h':H,'land':land,'contours':[out[i] for i in range(len(levels))],'proj':{'lon0':LON0,'lat0':LAT0,'s':S,'c':C},'pos':pos})+';'
open('assets/js/mapdata.js','w').write(js)
print(len(js), pos)
