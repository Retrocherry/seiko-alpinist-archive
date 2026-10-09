/* Interactive watch-and-sun direction finder.
   Model: northern hemisphere — point the hour hand at the sun; south lies halfway between the
   hour hand and 12. Southern hemisphere — point 12 at the sun; north lies halfway between 12 and
   the hour hand. On an Alpinist the inner compass ring is turned so "S" (or "N") sits on that bisector.
   All angles in degrees, clockwise from screen-up. */
(function(){
  const root=document.getElementById('compass-lab');if(!root)return;
  const NS='http://www.w3.org/2000/svg';
  const svg=root.querySelector('svg');
  const $=s=>root.querySelector(s);
  const st={hour:10.0,watch:0,ring:0,hemi:'N',dst:false,auto:true};
  // geometry
  const C=250,R=150;
  const el=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e;};
  const pol=(r,deg)=>{const a=(deg-90)*Math.PI/180;return[C+r*Math.cos(a),C+r*Math.sin(a)];};

  // ground compass (true directions)
  const ground=el('g',{class:'ground'});
  el('circle',{cx:C,cy:C,r:232,fill:'none',stroke:'currentColor','stroke-opacity':.18},ground);
  for(let d=0;d<360;d+=5){const[x1,y1]=pol(d%45?226:220,d),[x2,y2]=pol(232,d);el('line',{x1,y1,x2,y2,stroke:'currentColor','stroke-opacity':d%45?.2:.45},ground);}
  [['N',0],['E',90],['S',180],['W',270]].forEach(([t,d])=>{const[x,y]=pol(246,d);const tx=el('text',{x,y:y+4,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':12,fill:t==='N'?'#b3302b':'currentColor','fill-opacity':t==='N'?1:.6},ground);tx.textContent=t;});

  // sun
  const sunG=el('g',{class:'sun',tabindex:0,role:'slider','aria-label':'Sun direction','aria-valuemin':0,'aria-valuemax':359});
  const sunRay=el('line',{x1:C,y1:C,stroke:'#b89a5a','stroke-dasharray':'2 5','stroke-width':1},sunG);
  const sun=el('circle',{r:13,fill:'#e8c26a',stroke:'#b89a5a','stroke-width':1},sunG);
  const sunHalo=el('circle',{r:22,fill:'none',stroke:'#e8c26a','stroke-opacity':.5},sunG);

  // watch (rotates as a whole by st.watch)
  const watch=el('g',{class:'watch'});
  el('circle',{cx:C,cy:C,r:R+28,fill:'#26302b',stroke:'#7e837d','stroke-width':2},watch);
  // inner rotating compass ring
  const ring=el('g',{class:'ring',tabindex:0,role:'slider','aria-label':'Inner compass ring rotation','aria-valuemin':0,'aria-valuemax':359},watch);
  el('circle',{cx:C,cy:C,r:R+22,fill:'#1a2420'},ring);
  el('circle',{cx:C,cy:C,r:R+4,fill:'none',stroke:'#3c4a43'},ring);
  for(let d=0;d<360;d+=15){const[x1,y1]=pol(R+18,d),[x2,y2]=pol(R+(d%45?13:8),d);el('line',{x1,y1,x2,y2,stroke:'#cfc8b5','stroke-width':d%45?.8:1.2},ring);}
  [['N',0],['NE',45],['E',90],['SE',135],['S',180],['SW',225],['W',270],['NW',315]].forEach(([t,d])=>{
    const[x,y]=pol(R+13,d);const tx=el('text',{x,y:y+3.5,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':t.length>1?7.5:11,fill:t==='N'?'#e0574f':'#efe8d6',transform:`rotate(${d} ${x} ${y})`},ring);tx.textContent=t;
  });
  // degree markings revealed on hover
  const degs=el('g',{class:'deg',opacity:0,style:'transition:opacity .4s'},ring);
  for(let d=0;d<360;d+=30){if(d%45===0)continue;const[x,y]=pol(R+13,d);const tx=el('text',{x,y:y+3,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':6.5,fill:'#b89a5a',transform:`rotate(${d} ${x} ${y})`},degs);tx.textContent=d+'°';}
  ring.addEventListener('pointerenter',()=>degs.setAttribute('opacity',1));
  ring.addEventListener('pointerleave',()=>degs.setAttribute('opacity',0));
  // dial
  el('circle',{cx:C,cy:C,r:R,fill:'#1f4a3a'},watch);
  const dialG=el('g',{},watch);
  for(let h=0;h<60;h++){const d=h*6,[x1,y1]=pol(R-4,d),[x2,y2]=pol(R-(h%5?9:4),d);el('line',{x1,y1,x2,y2,stroke:'#efe8d6','stroke-opacity':h%5?.4:0,'stroke-width':.8},dialG);}
  for(let h=1;h<=12;h++){
    const d=h*30;
    if(h%3===0){const[x,y]=pol(R-26,d);el('path',{d:'M0 -14 L10 9 L-10 9Z',fill:'#efe8d6',transform:`translate(${x} ${y}) rotate(${d})`},dialG);} // mountain-peak cardinal markers
    else{const[x,y]=pol(R-22,d);const tx=el('text',{x,y:y+6,'text-anchor':'middle','font-family':'Shippori Mincho,serif','font-size':17,fill:'#efe8d6'},dialG);tx.textContent=h;}
  }
  const nm=el('text',{x:C,y:C-48,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':9,'letter-spacing':3,fill:'#efe8d6','fill-opacity':.75},dialG);nm.textContent='ALPINIST';
  // bisector
  const bis=el('line',{x1:C,y1:C,stroke:'#e0574f','stroke-width':1.4,'stroke-dasharray':'5 4'},watch);
  const bisLbl=el('text',{'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':10,fill:'#e0574f'},watch);
  // hands
  const hourH=el('g',{class:'hh',tabindex:0,role:'slider','aria-label':'Hour hand','aria-valuemin':0,'aria-valuemax':12},watch);
  el('path',{d:`M${C-4} ${C+14} L${C-6} ${C-60} L${C} ${C-88} L${C+6} ${C-60} L${C+4} ${C+14}Z`,fill:'#efe8d6',stroke:'#0f211a'},hourH);
  el('circle',{cx:C,cy:C-58,r:9,fill:'none',stroke:'#0f211a','stroke-width':2.4},hourH); // cathedral-style cut-out
  const minH=el('path',{d:`M${C-2.5} ${C+18} L${C-3} ${C-120} L${C} ${C-136} L${C+3} ${C-120} L${C+2.5} ${C+18}Z`,fill:'#efe8d6','fill-opacity':.85,stroke:'#0f211a'},watch);
  el('circle',{cx:C,cy:C,r:5,fill:'#b89a5a'},watch);

  const norm=a=>((a%360)+360)%360;
  function compute(){
    // The method reads the clock as shown. With DST in effect (and uncorrected) the clock runs
    // an hour ahead of solar time, so the result drifts — a real limitation we want to show.
    const hourAngle=norm(st.hour*30);             // hour hand on dial
    const minAngle=norm((st.hour%1)*360);
    // halfway between the hour hand and 12, taken the short way (morning bisects anticlockwise)
    const bisDial=norm(((st.hour-12)*30)/2);
    return{hourAngle,minAngle,bisDial};
  }
  function draw(){
    const g=compute();
    if(st.auto){ // keep watch aligned so reference points at sun (demonstrates the method)
      const ref=st.hemi==='N'?g.hourAngle:0;
      st.watch=norm(st.sun-ref);
      // the bisector of hour-hand/12 is "south" (N) or "north" (S); align ring so its S or N sits on it
      st.ring=norm(g.bisDial-(st.hemi==='N'?180:0));
    }
    watch.setAttribute('transform',`rotate(${st.watch} ${C} ${C})`);
    ring.setAttribute('transform',`rotate(${st.ring} ${C} ${C})`);
    hourH.setAttribute('transform',`rotate(${g.hourAngle} ${C} ${C})`);
    minH.setAttribute('transform',`rotate(${g.minAngle} ${C} ${C})`);
    const[bx,by]=pol(R-8,g.bisDial);bis.setAttribute('x2',bx);bis.setAttribute('y2',by);
    const[lx,ly]=pol(R-40,g.bisDial);bisLbl.setAttribute('x',lx);bisLbl.setAttribute('y',ly);
    bisLbl.textContent=st.hemi==='N'?'S':'N';
    bisLbl.setAttribute('transform',`rotate(${-st.watch} ${lx} ${ly})`);
    const[sx,sy]=pol(205,st.sun);sun.setAttribute('cx',sx);sun.setAttribute('cy',sy);sunHalo.setAttribute('cx',sx);sunHalo.setAttribute('cy',sy);
    sunRay.setAttribute('x2',sx);sunRay.setAttribute('y2',sy);
    // readouts
    const ringNorth=norm(st.watch+st.ring);       // where the ring's N points in the world
    const err=Math.round(Math.abs(((ringNorth+180)%360)-180));
    const hh=Math.floor(st.hour),mm=Math.round((st.hour%1)*60);
    $('#cl-time').textContent=`${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}`;
    $('#cl-sun').textContent=Math.round(st.sun)+'°';
    $('#cl-watch').textContent=Math.round(st.watch)+'°';
    $('#cl-ring').textContent=Math.round(st.ring)+'°';
    $('#cl-out').innerHTML=st.auto
      ? `Hour hand ${st.hemi==='N'?'pointed at the sun':'— 12 pointed at the sun'}. The ring's <b>N</b> now points to <b>${Math.round(ringNorth)}°</b> on the true compass. ${err<=8?'A close match to true north in this idealised sun position.':'Off from true north by about <b>'+err+'°</b> — because the sun is not where the simple 15°-per-hour rule assumes.'}`
      : `Manual mode — the ring's <b>N</b> points to <b>${Math.round(ringNorth)}°</b> (true north is 0°).`;
    ['hour','watch','ring','sun'].forEach(k=>{const i=$('#cl-'+k+'-in');if(i&&document.activeElement!==i)i.value=k==='hour'?st.hour:Math.round(st[k]);});
    hourH.setAttribute('aria-valuenow',st.hour.toFixed(1));ring.setAttribute('aria-valuenow',Math.round(st.ring));sunG.setAttribute('aria-valuenow',Math.round(st.sun));
  }
  // An idealised sun: azimuth 180 at 12:00 (N hemisphere), moving 15°/h — what the method assumes.
  function idealSun(){const h=st.dst?st.hour-1:st.hour;return st.hemi==='N'?norm(180+(h-12)*15):norm(0-(h-12)*15);}
  st.sun=idealSun();
  // inputs
  const bind=(id,fn)=>{const i=$(id);i&&i.addEventListener('input',()=>{fn(parseFloat(i.value));draw();});};
  bind('#cl-hour-in',v=>{st.hour=v;if($('#cl-follow').checked)st.sun=idealSun();});
  bind('#cl-sun-in',v=>{st.sun=v;$('#cl-follow').checked=false;});
  bind('#cl-watch-in',v=>{st.watch=v;st.auto=false;syncAuto();});
  bind('#cl-ring-in',v=>{st.ring=v;st.auto=false;syncAuto();});
  $('#cl-follow').addEventListener('change',e=>{if(e.target.checked){st.sun=idealSun();draw();}});
  $('#cl-auto').addEventListener('click',()=>{st.auto=!st.auto;syncAuto();draw();});
  function syncAuto(){$('#cl-auto').setAttribute('aria-pressed',st.auto);$('#cl-auto').textContent=st.auto?'Auto-solve: on':'Auto-solve: off';}
  root.querySelectorAll('[data-hemi]').forEach(b=>b.addEventListener('click',()=>{st.hemi=b.dataset.hemi;root.querySelectorAll('[data-hemi]').forEach(x=>x.setAttribute('aria-pressed',x===b));if($('#cl-follow').checked)st.sun=idealSun();$('#cl-method').innerHTML=st.hemi==='N'?METHOD_N:METHOD_S;draw();}));
  $('#cl-dst').addEventListener('change',e=>{st.dst=e.target.checked;draw();});
  const METHOD_N='<li><span>Hold the watch flat and turn it until the <b>hour hand</b> points at the sun.</span></li><li><span>South lies roughly halfway between the hour hand and 12.</span></li><li><span>Rotate the inner compass ring until <b>S</b> sits on that halfway line — the ring now reads all directions.</span></li>';
  const METHOD_S='<li><span>Hold the watch flat and point <b>12 o\'clock</b> at the sun.</span></li><li><span>North lies roughly halfway between 12 and the hour hand.</span></li><li><span>Rotate the inner compass ring until <b>N</b> sits on that halfway line.</span></li>';
  $('#cl-method').innerHTML=METHOD_N;
  // dragging
  function angleFrom(e){const r=svg.getBoundingClientRect();const x=(e.clientX-r.left)/r.width*500-C,y=(e.clientY-r.top)/r.height*500-C;return norm(Math.atan2(y,x)*180/Math.PI+90);}
  function drag(target,on){
    let start=null,base=0;
    target.style.cursor='grab';
    target.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();target.setPointerCapture(e.pointerId);start=angleFrom(e);base=on.get();target.style.cursor='grabbing';});
    target.addEventListener('pointermove',e=>{if(start===null)return;on.set(norm(base+angleFrom(e)-start));draw();});
    const end=()=>{start=null;target.style.cursor='grab';};
    target.addEventListener('pointerup',end);target.addEventListener('pointercancel',end);
    target.addEventListener('keydown',e=>{const k={ArrowRight:5,ArrowUp:5,ArrowLeft:-5,ArrowDown:-5}[e.key];if(k){e.preventDefault();on.set(norm(on.get()+k));draw();}});
  }
  drag(ring,{get:()=>st.ring,set:v=>{st.ring=v;st.auto=false;syncAuto();}});
  drag(sunG,{get:()=>st.sun,set:v=>{st.sun=v;$('#cl-follow').checked=false;}});
  drag(hourH,{get:()=>st.hour*30,set:v=>{st.hour=Math.round(v/30*12)/12;if(st.hour<6)st.hour+=12;if($('#cl-follow').checked)st.sun=idealSun();}});
  draw();
})();
