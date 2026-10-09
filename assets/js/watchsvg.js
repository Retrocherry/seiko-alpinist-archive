/* Schematic Alpinist renderer — parametric line drawings used for the design-evolution slider
   and as clearly-labelled placeholders. These are illustrations, never presented as photographs. */
(function(){
const P=(cx,cy,r,deg)=>{const a=(deg-90)*Math.PI/180;return[cx+r*Math.cos(a),cy+r*Math.sin(a)];};
function hands(kind,c,len,w){
  if(kind==='dauphine')return `<path d="M${c-w} ${c} L${c} ${c-len} L${c+w} ${c} L${c} ${c+len*.12}Z"/>`;
  if(kind==='sword')return `<path d="M${c-w*.5} ${c+len*.15} L${c-w} ${c-len*.75} L${c} ${c-len} L${c+w} ${c-len*.75} L${c+w*.5} ${c+len*.15}Z"/>`;
  if(kind==='baton')return `<rect x="${c-w*.55}" y="${c-len}" width="${w*1.1}" height="${len*1.12}" rx="1"/>`;
  // cathedral: stem + gothic lobed tip with cut-outs
  const t=c-len;
  return `<path d="M${c-w*.35} ${c+len*.14} L${c-w*.4} ${c-len*.45} C${c-w*1.5} ${c-len*.55} ${c-w*1.4} ${c-len*.85} ${c} ${t} C${c+w*1.4} ${c-len*.85} ${c+w*1.5} ${c-len*.55} ${c+w*.4} ${c-len*.45} L${c+w*.35} ${c+len*.14}Z"/><path d="M${c} ${c-len*.5} L${c-w*.6} ${c-len*.62} L${c} ${c-len*.86} L${c+w*.6} ${c-len*.62}Z" fill="rgba(0,0,0,.35)"/>`;
}
window.renderWatch=function(cfg,opts){
  cfg=Object.assign({dial:'#1f4a3a',tex:'sunburst',hands:'cathedral',idx:'alpinist',compass:true,date:'cyclops3',crowns:2,logo:'seiko',prospex:false,gmt:false,lume:'#efe8d6',metal:'#c9ccc6',accent:'#e0574f',size:1,time:[10,9,30],label:''},cfg||{});
  const S=400,c=200,R=118*cfg.size,ring=cfg.compass?R:R, dr=cfg.compass?R-18:R-4;
  const id='w'+Math.random().toString(36).slice(2,7);
  let s=`<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${(opts&&opts.aria)||'Schematic illustration of an Alpinist dial'}">`;
  s+=`<defs><radialGradient id="${id}d" cx="50%" cy="42%" r="65%"><stop offset="0" stop-color="${cfg.dial}" stop-opacity="1"/><stop offset="1" stop-color="${cfg.dial}" stop-opacity="1"/></radialGradient>
  <linearGradient id="${id}m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f0"/><stop offset=".45" stop-color="${cfg.metal}"/><stop offset="1" stop-color="#6c706a"/></linearGradient>
  <radialGradient id="${id}s" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient></defs>`;
  // lugs + strap stubs
  s+=`<g fill="url(#${id}m)" stroke="#2a2d2b" stroke-width=".8">`;
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([x,y])=>{s+=`<path d="M${c+x*R*.55} ${c+y*R*.78} L${c+x*R*.62} ${c+y*(R+44)} L${c+x*R*.36} ${c+y*(R+44)} L${c+x*R*.3} ${c+y*R*.8}Z"/>`;});
  s+=`</g>`;
  // crowns
  const cr=(deg,big,threads)=>{const[x,y]=P(c,c,R+12,deg);return `<g transform="translate(${x} ${y}) rotate(${deg-90})"><rect x="-${big?9:7}" y="-${big?11:9}" width="${big?18:14}" height="${big?22:18}" rx="2.5" fill="url(#${id}m)" stroke="#2a2d2b" stroke-width=".8"/>${threads?`<path d="M-6 -7v14M-2 -8v16M2 -8v16M6 -7v14" stroke="#555" stroke-width=".6"/>`:''}</g>`;};
  s+=cfg.crowns===2?cr(98,true,true)+cr(128,false,true):cr(90,true,cfg.idx!=='laurel');
  // case
  s+=`<circle cx="${c}" cy="${c}" r="${R+12}" fill="url(#${id}m)" stroke="#2a2d2b" stroke-width="1"/>`;
  s+=`<circle cx="${c}" cy="${c}" r="${R+3}" fill="#1a1c1b"/>`;
  // inner compass ring
  if(cfg.compass){
    s+=`<circle cx="${c}" cy="${c}" r="${R}" fill="${cfg.ringColor||'#1b1e1c'}"/>`;
    for(let d=0;d<360;d+=15){const[x1,y1]=P(c,c,R-2,d),[x2,y2]=P(c,c,R-(d%45?6:4),d);if(d%45)s+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${cfg.ringInk||'#d8d2c0'}" stroke-width=".8"/>`;}
    [['N',0],['NE',45],['E',90],['SE',135],['S',180],['SW',225],['W',270],['NW',315]].forEach(([t,d])=>{const[x,y]=P(c,c,R-8.5,d);s+=`<text x="${x}" y="${y+3}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="${t.length>1?6:8.5}" fill="${t==='N'?cfg.accent:(cfg.ringInk||'#d8d2c0')}" transform="rotate(${d} ${x} ${y})">${t}</text>`;});
  } else if(cfg.idx==='reinterp'){
    s+=`<circle cx="${c}" cy="${c}" r="${R}" fill="${cfg.dial}"/>`;
  }
  // dial
  s+=`<circle cx="${c}" cy="${c}" r="${dr}" fill="url(#${id}d)"/>`;
  if(cfg.tex==='sunburst'){for(let d=0;d<360;d+=3){const[x,y]=P(c,c,dr,d);s+=`<line x1="${c}" y1="${c}" x2="${x}" y2="${y}" stroke="#fff" stroke-opacity="${.02+.03*Math.abs(Math.sin(d*Math.PI/180*2))}" stroke-width=".7"/>`;}}
  if(cfg.tex==='vertical'){s+=`<clipPath id="${id}c"><circle cx="${c}" cy="${c}" r="${dr}"/></clipPath><g clip-path="url(#${id}c)">`;for(let x=c-dr;x<c+dr;x+=2.5)s+=`<line x1="${x}" y1="${c-dr}" x2="${x}" y2="${c+dr}" stroke="#fff" stroke-opacity="${.03+.04*Math.random()}"/>`;s+=`</g>`;}
  s+=`<circle cx="${c}" cy="${c}" r="${dr}" fill="url(#${id}s)"/>`;
  // minute track
  for(let m=0;m<60;m++){const d=m*6,[x1,y1]=P(c,c,dr-2,d),[x2,y2]=P(c,c,dr-(m%5?5:7),d);s+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${cfg.ink||'#efe8d6'}" stroke-opacity="${m%5?.45:.8}" stroke-width="${m%5?.6:1}"/>`;}
  // indices
  const ink=cfg.ink||'#efe8d6',gold=cfg.idxColor||ink;
  for(let h=1;h<=12;h++){
    const d=h*30,card=h%3===0;
    if(cfg.idx==='laurel'||cfg.idx==='reinterp'){
      const[x,y]=P(c,c,dr-(card?24:18),d);
      s+=card?`<path d="M0 -${cfg.idx==='laurel'?13:12} L9 8 L-9 8Z" fill="${cfg.lume}" stroke="${gold}" stroke-width="1" transform="translate(${x} ${y}) rotate(${d})"/>`
             :`<rect x="-2.6" y="-8" width="5.2" height="16" fill="${gold}" transform="translate(${x} ${y}) rotate(${d})"/>`;
    } else if(cfg.idx==='champion'){
      const[x,y]=P(c,c,dr-18,d),[x2,y2]=P(c,c,dr*.38,d);
      s+=`<line x1="${x}" y1="${y}" x2="${x2}" y2="${y2}" stroke="${gold}" stroke-opacity=".35" stroke-width=".7"/>`;
      s+=`<path d="M-4 -10 L4 -10 L3 9 L-3 9Z" fill="${cfg.lume}" stroke="${gold}" transform="translate(${x} ${y}) rotate(${d})"/>`;
    } else { // modern Alpinist: alternating arabic numerals + cardinal triangles
      if(card){const[x,y]=P(c,c,dr-22,d);s+=`<path d="M0 -11 L8 7 L-8 7Z" fill="${cfg.lume}" stroke="${gold}" transform="translate(${x} ${y}) rotate(${d})"/>`;}
      else if(!(cfg.date!=='none'&&h===3)){const[x,y]=P(c,c,dr-21,d);s+=`<text x="${x}" y="${y+5.5}" text-anchor="middle" font-family="Shippori Mincho,serif" font-size="15" fill="${gold}">${h}</text>`;}
    }
  }
  // date
  if(cfg.date!=='none'){
    const deg=cfg.date==='4'?120:90,[x,y]=P(c,c,dr-26,deg);
    s+=`<rect x="${x-9}" y="${y-7}" width="18" height="14" fill="#f4f1e8" transform="rotate(${cfg.date==='4'?30:0} ${x} ${y})"/><text x="${x}" y="${y+4}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="9" fill="#222" transform="rotate(${cfg.date==='4'?30:0} ${x} ${y})">${cfg.time[2]>15?'17':'3'}</text>`;
  }
  // text
  const logoY=c-dr*.48;
  s+=`<text x="${c}" y="${logoY}" text-anchor="middle" font-family="Helvetica Neue,Arial,sans-serif" font-weight="700" font-size="11" letter-spacing="2.5" fill="${ink}">SEIKO</text>`;
  if(cfg.prospex)s+=`<path d="M${c-5} ${logoY+6} l10 10 M${c+5} ${logoY+6} l-10 10" stroke="${ink}" stroke-width="1.6"/>`;
  if(cfg.laurelText)s+=`<text x="${c}" y="${logoY+13}" text-anchor="middle" font-family="Shippori Mincho,serif" font-style="italic" font-size="8" fill="${ink}">Laurel</text>`;
  s+=`<text x="${c}" y="${c+dr*.42}" text-anchor="middle" font-family="Shippori Mincho,serif" font-style="italic" font-size="12" fill="${cfg.alpColor||cfg.accent}">Alpinist</text>`;
  if(cfg.subText)s+=`<text x="${c}" y="${c+dr*.55}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="5.5" letter-spacing="1" fill="${ink}" fill-opacity=".7">${cfg.subText}</text>`;
  // hands
  const[hh,mm]=cfg.time;
  const hc=cfg.handColor||ink;
  s+=`<g fill="${hc}" stroke="#111" stroke-width=".5">`;
  if(cfg.gmt)s+=`<g transform="rotate(${(hh*15+mm*.25)%360} ${c} ${c})"><line x1="${c}" y1="${c}" x2="${c}" y2="${c-dr+16}" stroke="${cfg.accent}" stroke-width="1.6"/><path d="M${c} ${c-dr+8} l6 11 h-12z" fill="${cfg.accent}"/></g>`;
  s+=`<g transform="rotate(${(hh%12)*30+mm*.5} ${c} ${c})">${hands(cfg.hands,c,dr*.55,7)}</g>`;
  s+=`<g transform="rotate(${mm*6} ${c} ${c})">${hands(cfg.hands==='cathedral'?'cathedral':cfg.hands,c,dr*.82,5.2)}</g>`;
  s+=`</g><g transform="rotate(${(cfg.time[2]||0)*6} ${c} ${c})"><line x1="${c}" y1="${c+22}" x2="${c}" y2="${c-dr+6}" stroke="${cfg.secColor||cfg.accent}" stroke-width="1"/></g>`;
  s+=`<circle cx="${c}" cy="${c}" r="4" fill="${hc}" stroke="#111" stroke-width=".5"/>`;
  // cyclops
  if(cfg.date==='cyclops3'){const[x,y]=P(c,c,dr-26,90);s+=`<circle cx="${x}" cy="${y}" r="12" fill="#fff" fill-opacity=".1" stroke="#fff" stroke-opacity=".35"/>`;}
  // crystal glare
  s+=`<path d="M${c-dr*.8} ${c-dr*.3} A${dr} ${dr} 0 0 1 ${c+dr*.3} ${c-dr*.85}" stroke="#fff" stroke-opacity=".12" stroke-width="16" fill="none"/>`;
  s+=`</svg>`;
  return s;
};
})();
