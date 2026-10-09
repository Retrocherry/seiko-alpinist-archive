/* Individual watch pages: schematic fallback, movement rotor reveal, nav state, slow landscape drift. */
(function(){
  const $=s=>document.querySelector(s);
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const host=$('[data-schem]');
  if(host)host.innerHTML=window.renderWatch(window.SCHEM||{},{aria:'Schematic illustration (not a photograph)'});
  // movement mini-diagram: tap/hover to swing the rotor and reveal the bridge beneath
  const mv=$('.mv-mini');
  if(mv){
    mv.innerHTML=`<svg viewBox="0 0 200 200" role="img" aria-label="Stylised automatic movement; the rotor swings aside on hover">
      <circle cx="100" cy="100" r="92" fill="#1a1d1b" stroke="#7e837d"/>
      <g stroke="#b89a5a" fill="none" stroke-width="1">
        <circle cx="100" cy="100" r="22"/><circle cx="100" cy="100" r="5" fill="#b3302b" stroke="none"/>
        <circle cx="140" cy="128" r="18"/><path d="M140 110 A18 18 0 0 1 158 128" stroke-dasharray="2 3"/>
        <circle cx="62" cy="132" r="14"/><circle cx="62" cy="132" r="3" fill="#b3302b" stroke="none"/>
        <path d="M40 70 C70 52 130 52 160 70" stroke="#7e837d"/><path d="M45 160 L80 120 L120 150 L155 108" stroke="#7e837d"/>
        <circle cx="122" cy="60" r="3" fill="#b3302b" stroke="none"/><circle cx="78" cy="58" r="3" fill="#b3302b" stroke="none"/>
      </g>
      <g class="rot" style="transform-origin:100px 100px;transition:transform 1.4s cubic-bezier(.3,.7,.2,1)">
        <path d="M100 100 L18 100 A82 82 0 0 1 182 100Z" fill="url(#rg)" stroke="#9aa09a"/>
        <text x="100" y="58" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="8" fill="#2a2d2b" letter-spacing="2">${(document.querySelector('.mvbox')?.dataset.cal||'').toUpperCase()}</text>
        <circle cx="100" cy="100" r="9" fill="#d8d8d2" stroke="#555"/>
      </g>
      <defs><linearGradient id="rg" x1="0" x2="1"><stop offset="0" stop-color="#e6e7e2"/><stop offset=".5" stop-color="#a9ada6"/><stop offset="1" stop-color="#d8d9d4"/></linearGradient></defs></svg>`;
    const rot=mv.querySelector('.rot');let a=0;
    const swing=()=>{a=a?0:200;rot.style.transform=`rotate(${a}deg)`;};
    mv.parentElement.addEventListener('mouseenter',swing);mv.parentElement.addEventListener('mouseleave',swing);
    mv.parentElement.addEventListener('click',e=>{if(!e.target.closest('a'))swing();});
  }
  const nav=$('.nav');
  addEventListener('scroll',()=>{nav.classList.toggle('solid',scrollY>40);
    const l=$('.w-land img');if(l&&!reduce&&scrollY<innerHeight*1.3)l.style.transform=`translate3d(0,${scrollY*.22}px,0) scale(1.06)`;},{passive:true});
  $('.menu-btn')?.addEventListener('click',e=>{const u=$('.nav ul');const o=u.classList.toggle('open');e.currentTarget.setAttribute('aria-expanded',o);});
})();
