/* Site search: a dialog over every reference (ref, nickname, series, dial, year, calibre).
   Index: window.ALP_SEARCH from assets/js/search-index.js. Open with the header button or "/". */
(function(){
  const IDX=window.ALP_SEARCH||[],base=document.body.dataset.base||'';
  const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const dlg=document.createElement('dialog');dlg.className='srch';dlg.setAttribute('aria-label','Search the archive');
  dlg.innerHTML=`<form method="dialog" class="srch-in" role="search" onsubmit="return false">
    <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>
    <label class="vh" for="srch-q">Search references</label>
    <input id="srch-q" type="search" placeholder="Search SPB249, Deep Lake, 6R35, green, 1995…" autocomplete="off" spellcheck="false" aria-controls="srch-list">
    <button type="button" class="srch-x" aria-label="Close search">Esc</button></form>
    <ul class="srch-list" id="srch-list" role="listbox" aria-label="Results"></ul>
    <p class="srch-foot mono">${IDX.length} references · ↑↓ to move · Enter to open</p>`;
  document.body.appendChild(dlg);
  const q=dlg.querySelector('input'),list=dlg.querySelector('ul');let hits=[],sel=0;
  const norm=s=>String(s||'').toLowerCase().normalize('NFKD').replace(/[^\w\s]/g,' ');
  function score(r,terms){
    let sc=0;
    for(const t of terms){
      const ref=r.ref.toLowerCase();
      if(ref===t||ref.replace(/j1?$/,'')===t)sc+=100;
      else if(ref.startsWith(t))sc+=60;
      else if((r.nick||'').toLowerCase().includes(t))sc+=40;
      else if(r.hay.includes(t))sc+=10;
      else return 0;
    }
    return sc;
  }
  function render(){
    const terms=norm(q.value).split(/\s+/).filter(Boolean);
    hits=(terms.length?IDX.map(r=>[score(r,terms),r]).filter(x=>x[0]).sort((a,b)=>b[0]-a[0]||(a[1].year||0)-(b[1].year||0)).map(x=>x[1]):IDX.slice().sort((a,b)=>(b.year||0)-(a.year||0))).slice(0,12);
    sel=Math.min(sel,Math.max(0,hits.length-1));
    list.innerHTML=hits.length?hits.map((r,i)=>`<li role="option" aria-selected="${i===sel}" id="srch-o${i}"><a href="${base}watches/${r.id}.html">
      <span class="sw" style="--sw:${r.dialHex}"></span>
      <span class="t"><b>${esc(r.ref)}</b>${r.nick?` <i>“${esc(r.nick)}”</i>`:''}<small>${esc(r.series)} · ${r.year||'—'}${r.cal?' · '+esc(r.cal):''}</small></span>
      <span class="st ${r.status}">${r.status==='current'?'Current':r.status==='limited'?'Limited':'Disc.'}</span></a></li>`).join('')
      :`<li class="none">No references match “${esc(q.value)}”.</li>`;
    q.setAttribute('aria-activedescendant',hits.length?'srch-o'+sel:'');
  }
  function open(){if(!dlg.open){dlg.showModal();q.value='';sel=0;render();q.focus();}}
  q.addEventListener('input',()=>{sel=0;render();});
  q.addEventListener('keydown',e=>{
    if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();sel=(sel+(e.key==='ArrowDown'?1:-1)+hits.length)%Math.max(1,hits.length);render();list.children[sel]?.scrollIntoView({block:'nearest'});}
    if(e.key==='Enter'&&hits[sel]){location.href=base+'watches/'+hits[sel].id+'.html';}
  });
  dlg.querySelector('.srch-x').onclick=()=>dlg.close();
  dlg.addEventListener('click',e=>{if(e.target===dlg)dlg.close();});
  document.addEventListener('click',e=>{if(e.target.closest('[data-search]'))open();});
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();open();}});
})();
