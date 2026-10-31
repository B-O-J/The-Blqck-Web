/* BLQCK — menu, slow reveals, gentle parallax, the dawn, the ring. No dependencies. */
(() => {
  const d = document, h = d.documentElement, $ = s => [...d.querySelectorAll(s)];
  const rm = matchMedia('(prefers-reduced-motion: reduce)').matches, cl = v => Math.max(0, Math.min(1, v));
  h.classList.replace('no-js', 'js');

  const btn = $('.mbtn')[0], menu = $('.menu')[0];
  if (btn && menu) {
    const set = o => {
      menu.classList.toggle('open', o); btn.setAttribute('aria-expanded', o);
      $('main,footer').forEach(n => n.inert = o); h.style.overflow = o ? 'hidden' : '';
      if (o) menu.querySelector('a').focus(); else btn.focus();
    };
    btn.onclick = () => set(!menu.classList.contains('open'));
    d.addEventListener('keydown', e => e.key === 'Escape' && menu.classList.contains('open') && set(false));
    menu.addEventListener('click', e => e.target.closest('a[aria-current]') && set(false));
  }

  const io = new IntersectionObserver(es => es.forEach((e, i) => {
    if (!e.isIntersecting) return;
    e.target.style.transitionDelay = Math.min(i * 120, 480) + 'ms';
    e.target.classList.add('in'); io.unobserve(e.target);
  }), { rootMargin: '0px 0px -10% 0px' });
  $('[data-r]').forEach(n => io.observe(n));

  const hero = $('.hero')[0], atm = $('.atmos')[0], bar = $('.prog')[0], flame = $('.flame')[0],
        dawn = $('[data-dawn]')[0], ring = $('.ring[data-draw]')[0];
  let raf = 0;
  const tick = () => {
    raf = 0;
    const y = scrollY, H = innerHeight, max = h.scrollHeight - H, p = max > 0 ? y / max : 0;
    if (bar) bar.style.transform = `scaleX(${p})`;
    if (flame) flame.style.setProperty('--flame', p.toFixed(3));
    if (ring) ring.style.setProperty('--draw', cl((H * .95 - ring.getBoundingClientRect().top) / (H * .8)).toFixed(3));
    if (!rm && hero) { const f = cl(y / (H * .8)); hero.style.setProperty('--f', f); atm.style.setProperty('--f2', f); }
    if (dawn) {
      const t = cl((H * .9 - dawn.getBoundingClientRect().top) / (H * .6));
      atm.style.setProperty('--dawn', t.toFixed(3)); h.classList.toggle('is-dawn', t > .55);
    }
  };
  addEventListener('scroll', () => raf || (raf = requestAnimationFrame(tick)), { passive: true });
  addEventListener('resize', tick); tick();

  // Fallback page fade for browsers without cross-document view transitions
  if (!('CSSViewTransitionRule' in window) && !rm) {
    d.addEventListener('click', e => {
      const a = e.target.closest('a[href]');
      if (!a || a.target || a.origin !== location.origin || (a.pathname === location.pathname && a.hash) || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault(); h.classList.add('leaving'); setTimeout(() => location.href = a.href, 550);
    });
    addEventListener('pageshow', e => e.persisted && h.classList.remove('leaving'));
  }
})();
