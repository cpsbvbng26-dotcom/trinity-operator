#!/usr/bin/env node
/* Tells the search engines that take IndexNow (Bing, Yandex, Naver, Seznam and others) which pages of the conjecture's
 * site are new or gone. It is the small version of cpsbvbng26-dotcom's verification/indexnow.js, set to this site.
 *
 * The key sits in site/<key>.txt, which Vercel serves at the root of the site; the file holds the key itself, as
 * IndexNow asks. The key is not a secret. Google does not take IndexNow; it reads the sitemap, which robots.txt names.
 *
 * Run by .github/workflows/indexnow.yml on each push to main that changes site/sitemap.xml.
 *   BEFORE=<commit>  compare the sitemap with the one at that commit (the push's previous head)
 *   ALL=yes          send every page of the sitemap
 *   node tools/indexnow.js --dry-run   # print what would be sent; send nothing
 *
 * The sitemap carries no <lastmod>, so a push tells only the pages that came into it or left it. A page whose text
 * changed is told by running the workflow by hand with all set to yes.
 * It waits until the deployment serves the key file, for up to ten minutes, before it sends anything.
 */
'use strict';
const ua = require('./ua.js');

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const SITE = path.join(ROOT, 'site');
const BASE = 'https://golden-window-conjecture.vercel.app/';
const KEY = fs.readdirSync(SITE).map((f) => /^([0-9a-f]{32})\.txt$/.exec(f)).filter(Boolean).map((m) => m[1])[0];
const DRY = process.argv.includes('--dry-run');

/* Pure: the <loc> and <lastmod> of each entry of a sitemap. */
const entries = (xml) => new Map([...String(xml || '').matchAll(/<loc>([^<]+)<\/loc>\s*(?:<lastmod>([^<]+)<\/lastmod>)?/g)].map((m) => [m[1], m[2] || '']));

function before(at) {
  if (!at || /^0+$/.test(at)) return '';
  if (!/^[0-9a-f]{7,40}$/.test(at)) throw new Error('BEFORE must be a commit id');
  try {
    return execFileSync('git', ['show', at + ':site/sitemap.xml'], { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  } catch (e) {
    return '';
  }
}

(async () => {
  if (!KEY || fs.readFileSync(path.join(SITE, KEY + '.txt'), 'utf8').trim() !== KEY) throw new Error('site/<key>.txt is missing, or does not hold the key');
  const now = entries(fs.readFileSync(path.join(SITE, 'sitemap.xml'), 'utf8'));
  const was = entries(before(process.env.BEFORE));
  const all = process.env.ALL === 'yes';
  const urls = [...now].filter(([u, d]) => all || was.get(u) !== d).map(([u]) => u)
    .concat([...was.keys()].filter((u) => !now.has(u)));
  if (urls.some((u) => !u.startsWith(BASE))) throw new Error('the sitemap names a page outside ' + BASE);
  console.log((all ? 'every page' : 'new or gone') + ': ' + urls.length);
  urls.forEach((u) => console.log('  ' + (now.has(u) ? '' : 'gone ') + u));
  if (DRY || !urls.length) return;
  for (let i = 0; i < 20; i++) {
    const r = await ua.request(BASE + KEY + '.txt', { cache: 'no-store', signal: AbortSignal.timeout(20000) }).catch(() => null);
    if (r && r.ok && (await r.text()).trim() === KEY) break;
    if (i === 19) throw new Error(BASE + KEY + '.txt does not serve the key; nothing was sent');
    await new Promise((ok) => setTimeout(ok, 30000));
  }
  const r = await ua.request('https://api.indexnow.org/indexnow', {
    method: 'POST', headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ host: new URL(BASE).host, key: KEY, keyLocation: BASE + KEY + '.txt', urlList: urls }),
  });
  console.log('IndexNow: HTTP ' + r.status);
  if (r.status !== 200 && r.status !== 202) process.exit(1);
})().catch((e) => { console.error(e.message); process.exit(1); });
