/* Shared production-only analytics. Never send form fields. */
(() => {
  if (location.hostname !== 'www.piste-ai.com' || window.pisteAnalyticsLoaded) return;
  window.pisteAnalyticsLoaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  const campaign = new URLSearchParams();
  const query = new URLSearchParams(location.search || '');
  for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_id', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid']) {
    if (query.has(key)) campaign.set(key, query.get(key));
  }
  const cleanLocation = location.origin + location.pathname + (campaign.size ? '?' + campaign : '');
  window.gtag('js', new Date());
  window.gtag('config', 'G-LR35246V7B', { page_location: cleanLocation, page_referrer: document.referrer.split('?')[0].split('#')[0] });
  const ga = document.createElement('script');
  ga.async = true;
  ga.src = 'https://www.googletagmanager.com/gtag/js?id=G-LR35246V7B';
  document.head.append(ga);
  window.clarity = window.clarity || function () { (window.clarity.q = window.clarity.q || []).push(arguments); };
  const heatmap = document.createElement('script');
  heatmap.async = true;
  heatmap.src = 'https://www.clarity.ms/tag/w54yutjekb';
  document.head.append(heatmap);
  const allowed = new Set(['generate_lead', 'line_click', 'coconala_click', 'begin_checkout']);
  window.pisteTrack = (name, parameters = {}) => {
    if (!allowed.has(name)) return;
    const safe = { page_location: cleanLocation };
    if (parameters.method === 'contact_form') safe.method = 'contact_form';
    window.gtag('event', name, safe);
    window.clarity('event', name);
  };
  document.addEventListener('click', event => {
    const anchor = event.target.closest?.('a[href]');
    if (!anchor) return;
    let url;
    try { url = new URL(anchor.href); } catch { return; }
    if (['lin.ee', 'line.me'].includes(url.hostname)) window.pisteTrack('line_click');
    else if (url.hostname === 'coconala.com') window.pisteTrack('coconala_click');
    else if (url.hostname === 'buy.stripe.com') window.pisteTrack('begin_checkout');
  });
})();
