/* Custom line-icon system — 24px grid, 1px hairline, round caps. Drawn for this archive. */
(function(){
const I={
 automatic:'<circle cx="12" cy="12" r="9"/><path d="M12 12V3M12 12l6.4 6.4"/><path d="M12 3a9 9 0 0 1 9 9H12z" fill="currentColor" fill-opacity=".18"/><circle cx="12" cy="12" r="1"/>',
 manual:'<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/><path d="M20 12h3M21.5 10.5v3"/>',
 quartz:'<path d="M9 3v8a3 3 0 0 0 6 0V3"/><path d="M12 14v7M8 21h8"/><path d="M5 6c1.2 1 1.2 3 0 4M19 6c-1.2 1-1.2 3 0 4"/>',
 movement:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/><circle cx="12" cy="12" r="7.5"/>',
 hacking:'<circle cx="12" cy="13" r="8"/><path d="M12 13V6"/><path d="M9 2h6M12 2v3"/><rect x="10" y="11" width="4" height="4" fill="currentColor" fill-opacity=".2"/>',
 gmt:'<circle cx="12" cy="12" r="9"/><path d="M12 12l5-5"/><path d="M12 12V6.5"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18" opacity=".55"/><path d="M17 7l1.6-1.6" />',
 compass:'<circle cx="12" cy="12" r="9"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2"/><path d="M15.5 8.5L13.2 13.2 8.5 15.5 10.8 10.8z" fill="currentColor" fill-opacity=".18"/>',
 compassbezel:'<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6.2"/><path d="M12 2v3.8M12 18.2V22M2 12h3.8M18.2 12H22"/><path d="M12 2.6l1.1 2.6h-2.2z" fill="currentColor"/><path d="M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" opacity=".6"/>',
 sapphire:'<path d="M6 4h12l4 5-10 12L2 9z"/><path d="M2 9h20M8 9l4 12 4-12M6 4l2 5M18 4l-2 5M12 4l-4 5M12 4l4 5"/>',
 hardlex:'<path d="M3 15c3-5 15-5 18 0"/><path d="M3 15v2h18v-2"/><path d="M7 11.5c2-1 8-1 10 0" opacity=".5"/>',
 acrylic:'<path d="M3 14c2-7 16-7 18 0"/><path d="M3 14v2.5h18V14"/><path d="M8 9.5c1.5-.6 6.5-.6 8 0" opacity=".5"/>',
 crown:'<rect x="9" y="3" width="6" height="18" rx="1"/><path d="M9 7h6M9 10h6M9 13h6M9 16h6M9 19h6" opacity=".6"/>',
 screwdown:'<rect x="8" y="5" width="8" height="14" rx="1"/><path d="M8 8l8 2M8 11l8 2M8 14l8 2" opacity=".7"/><path d="M12 5V2M10 3h4"/><circle cx="12" cy="21.5" r=".5"/>',
 caseback:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="6"/><path d="M12 6l3 6-3 6-3-6z" opacity=".7"/><path d="M5.6 5.6l1.2 1.2M17.2 17.2l1.2 1.2M18.4 5.6l-1.2 1.2M6.8 17.2l-1.2 1.2" opacity=".5"/>',
 lume:'<circle cx="12" cy="12" r="3.2"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',
 water:'<path d="M2 9c2.5-2 4.5-2 7 0s4.5 2 7 0 4-1.6 6-.4"/><path d="M2 14c2.5-2 4.5-2 7 0s4.5 2 7 0 4-1.6 6-.4"/><path d="M12 17v5M10 20l2 2 2-2"/>',
 magnet:'<path d="M5 3v9a7 7 0 0 0 14 0V3"/><path d="M5 3h4v9a3 3 0 0 0 6 0V3h4"/><path d="M5 7h4M15 7h4"/>',
 date:'<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 9h18"/><text x="12" y="17" font-size="6" text-anchor="middle" fill="currentColor" stroke="none" font-family="IBM Plex Mono,monospace">3</text>',
 cyclops:'<rect x="3" y="7" width="18" height="10" rx="1"/><circle cx="12" cy="12" r="3.6" fill="currentColor" fill-opacity=".12"/><path d="M12 8.4v7.2" opacity=".5"/>',
 limited:'<rect x="3" y="6" width="18" height="12" rx="1"/><path d="M7 10v4M6 11l1-1M11 10h3M11 12h3M11 14h3" opacity=".8"/><path d="M17 9v6" opacity=".4"/>',
 jp:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.6" fill="currentColor" fill-opacity=".85"/>',
 global:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3.5 3.5 3.5 14.5 0 18M12 3c-3.5 3.5-3.5 14.5 0 18"/>',
 dia:'<circle cx="12" cy="12" r="8"/><path d="M2 12h3M19 12h3M4 10l-2 2 2 2M20 10l2 2-2 2"/>',
 thick:'<path d="M4 9h16v6H4z"/><path d="M22 6v12M20 8l2-2 2 2M20 16l2 2 2-2" transform="translate(-3 0)"/>',
 lug:'<path d="M6 4h12M6 20h12M12 4v16M9 7l3-3 3 3M9 17l3 3 3-3"/>',
 power:'<path d="M4 17a8 8 0 0 1 16 0"/><path d="M12 17l4-5"/><path d="M6 17h1M17 17h1M12 9v1" opacity=".7"/><circle cx="12" cy="17" r="1"/>',
 mountain:'<path d="M2 20l6.5-11 3 5 3.5-7L22 20z"/><path d="M6 20l2.5-4M14 20l2-3" opacity=".5"/>',
 strap:'<rect x="8" y="8" width="8" height="8" rx="1.5"/><path d="M9 8l.8-5h4.4l.8 5M9 16l.8 5h4.4l.8-5"/>',
 ext:'<path d="M7 17L17 7M9 7h8v8"/>',
 close:'<path d="M5 5l14 14M19 5L5 19"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',
 check:'<path d="M5 12.5l4.5 4.5L19 7.5"/>',
 watch:'<circle cx="12" cy="12" r="6"/><path d="M12 9v3l2 1.5M9 6l.8-3h4.4l.8 3M9 18l.8 3h4.4l.8-3"/>'
};
window.ICONS=I;
window.ico=(n,c)=>`<svg class="ico ${c||''}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${I[n]||I.movement}</svg>`;
const hyd=()=>document.querySelectorAll('i[data-ico]').forEach(e=>{e.outerHTML=window.ico(e.dataset.ico,e.className.replace(/^i\b/,''));});
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',hyd):hyd();
})();
