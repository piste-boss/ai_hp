const endpoint = 'https://script.google.com/macros/s/AKfycby4Tn3NHhyIVd_3gQzGT6bfF2EP9Q6bZ2IMLET5BE_ttVZCLBlC8yz5JpXOS_JAE6pi/exec';
const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }
});

export default async function contact(req) {
  if (req.method !== 'POST') return json({ status: 'error' }, 405);
  const origin = req.headers.get('origin');
  if (origin && origin !== new URL(req.url).origin) return json({ status: 'error' }, 403);
  if (!req.headers.get('content-type')?.startsWith('application/json')) return json({ status: 'error' }, 415);
  let data;
  try {
    const raw = await req.text();
    if (raw.length > 16000) return json({ status: 'error' }, 413);
    const input = JSON.parse(raw);
    if (!input || typeof input !== 'object' || input.website) return json({ status: 'error' }, 400);
    data = {};
    for (const [key, max] of Object.entries({ name: 100, company: 200, email: 254, category: 100, message: 5000 })) {
      if (typeof input[key] !== 'string' || input[key].length > max) return json({ status: 'error' }, 400);
      data[key] = input[key].trim();
    }
    if (!data.name || !data.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) return json({ status: 'error' }, 400);
  } catch { return json({ status: 'error' }, 400); }
  try {
    const upstream = await fetch(endpoint, {
      method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(data), signal: AbortSignal.timeout(25000)
    });
    if (!upstream.ok || (await upstream.json()).status !== 'ok') return json({ status: 'error' }, 502);
    return json({ status: 'ok' });
  } catch { return json({ status: 'error' }, 502); }
}

export const config = { path: '/api/contact' };
