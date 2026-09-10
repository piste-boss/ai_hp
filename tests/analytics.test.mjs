import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const code = fs.readFileSync(new URL('../site/js/analytics.js', import.meta.url), 'utf8');
function environment(hostname) {
  const scripts = [], listeners = {};
  const sandbox = { URL, URLSearchParams, Set, Date, location: { hostname, origin: `https://${hostname}`, pathname: '/blog/test', search: '?utm_source=google&email=private' },
    document: { referrer: 'https://referrer.example/?email=private#x', head: { append: script => scripts.push(script) },
      createElement: () => ({}), addEventListener: (name, handler) => { listeners[name] = handler; } } };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  return { sandbox, scripts, listeners };
}
test('preview does not load or send production measurement', () => {
  const e = environment('preview--piste-ai.netlify.app');
  vm.runInContext(code, e.sandbox);
  assert.equal(e.scripts.length, 0);
  assert.equal(e.sandbox.gtag, undefined);
});
test('production initializes once, strips private parameters and counts one click', () => {
  const e = environment('www.piste-ai.com');
  vm.runInContext(code, e.sandbox); vm.runInContext(code, e.sandbox);
  assert.equal(e.scripts.length, 2);
  assert.equal(e.sandbox.dataLayer.filter(x => x[0] === 'config').length, 1);
  assert.equal(e.sandbox.dataLayer[1][2].page_location, 'https://www.piste-ai.com/blog/test?utm_source=google');
  e.listeners.click({ target: { closest: () => ({ href: 'https://lin.ee/Pul5f6V' }) } });
  assert.equal(e.sandbox.dataLayer.filter(x => x[1] === 'line_click').length, 1);
  e.sandbox.pisteTrack('generate_lead', { email: 'private@example.com', method: 'contact_form' });
  assert.equal(JSON.stringify(e.sandbox.dataLayer).includes('private'), false);
  assert.equal(e.sandbox.dataLayer.filter(x => x[1] === 'generate_lead').length, 1);
});
