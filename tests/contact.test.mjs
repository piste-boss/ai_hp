import test from 'node:test';
import assert from 'node:assert/strict';
import contact from '../site/netlify/functions/contact.mjs';

const body = { name: 'Test', company: '', email: 'test@example.com', category: 'general', message: 'Test message', website: '' };
const request = (data = body, origin = 'https://www.piste-ai.com') => new Request('https://www.piste-ai.com/api/contact', {
  method: 'POST', headers: { 'Content-Type': 'application/json', origin }, body: JSON.stringify(data)
});
test('validation rejects bad data without forwarding', async () => {
  const old = global.fetch;
  global.fetch = () => { throw new Error('must not forward'); };
  try {
    assert.equal((await contact(request({ ...body, email: 'invalid' }))).status, 400);
    assert.equal((await contact(request({ ...body, website: 'spam' }))).status, 400);
    assert.equal((await contact(request(body, 'https://unrelated.example'))).status, 403);
  } finally { global.fetch = old; }
});
test('success requires a positive upstream acknowledgement', async () => {
  const old = global.fetch;
  try {
    for (const [result, expected] of [[{ status: 'ok' }, 200], [{ status: 'error' }, 502], [{}, 502]]) {
      global.fetch = async (_url, opts) => {
        assert.equal(JSON.parse(opts.body).email, body.email);
        assert.equal(JSON.parse(opts.body).type, undefined);
        return Response.json(result);
      };
      assert.equal((await contact(request())).status, expected);
    }
    global.fetch = async () => { throw new Error('timeout'); };
    assert.equal((await contact(request())).status, 502);
  } finally { global.fetch = old; }
});
