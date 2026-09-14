(() => {
  const art = document.querySelector('.p3-art');
  if (!art) return;
  const button = art.querySelector('.p3-motion');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  let paused = reduced.matches;
  let visible = true;
  function sync() {
    art.classList.toggle('p3-paused', paused || !visible || document.hidden);
    button.setAttribute('aria-pressed', String(paused));
    button.textContent = paused ? '動きを再開する' : '動きを止める';
    button.hidden = reduced.matches;
  }
  button.addEventListener('click', () => { paused = !paused; sync(); });
  reduced.addEventListener('change', () => { paused = reduced.matches; sync(); });
  document.addEventListener('visibilitychange', sync);
  new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }).observe(art);
  art.addEventListener('pointermove', event => {
    if (paused || reduced.matches || !fine.matches) return;
    const box = art.getBoundingClientRect();
    art.style.setProperty('--p3-x', `${-19 - ((event.clientY - box.top) / box.height - .5) * 12}deg`);
    art.style.setProperty('--p3-y', `${-32 + ((event.clientX - box.left) / box.width - .5) * 24}deg`);
  });
  art.addEventListener('pointerleave', () => {
    art.style.removeProperty('--p3-x');
    art.style.removeProperty('--p3-y');
  });
  sync();
})();
