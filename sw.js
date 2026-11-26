'use strict';
const PREFIX = 'laos-outing:' + self.registration.scope + ':';
const CACHE = PREFIX + 'v13';
const ROOT = self.registration.scope;
const READY = new URL('__offline-ready', ROOT).href;
const PAGES = ['index.html', 'before-departure.html', 'transfers.html', 'night.html', 'tickets.html'];
const CORE = [...PAGES, 'pwa.js', 'pwa.css', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png'];
let saving;

// Discover document links in the pages, so newly linked source images are saved too.
async function saveBundle() {
  if (saving) return saving;
  saving = (async () => {
    const cache = await caches.open(CACHE);
    const files = new Set();
    const responses = await Promise.all(CORE.map(async path => {
      const url = new URL(path, ROOT).href;
      const response = await fetch(url, {cache: 'reload'});
      if (!response.ok) throw new Error('ดาวน์โหลดไม่สำเร็จ');
      await response.clone().arrayBuffer();
      if (PAGES.includes(path)) {
        const html = await response.clone().text();
        for (const match of html.matchAll(/(?:href|src)\s*=\s*["']([^"']+)["']/gi)) {
          const asset = new URL(match[1].replace(/&amp;/g, '&'), url);
          if (asset.origin === self.location.origin && asset.pathname.startsWith(new URL('source/', ROOT).pathname)) {
            asset.hash = '';
            files.add(asset.href);
          }
        }
      }
      return [url, response];
    }));
    const images = await Promise.all([...files].map(async url => {
      const response = await fetch(url, {cache: 'reload'});
      if (!response.ok) throw new Error('ดาวน์โหลดรูปไม่ครบ');
      await response.clone().arrayBuffer();
      return [url, response];
    }));
    // Only replace saved responses after every download has succeeded.
    await Promise.all([...responses, ...images].map(([url, response]) => cache.put(url, response)));
    const status = {ready: true, images: files.size, savedAt: Date.now()};
    await cache.put(READY, new Response(JSON.stringify(status), {headers: {'Content-Type': 'application/json'}}));
    return status;
  })();
  try { return await saving; } finally { saving = null; }
}

self.addEventListener('install', event => {
  event.waitUntil(saveBundle().then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith(PREFIX) && name !== CACHE) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});
self.addEventListener('message', event => {
  const port = event.ports[0];
  if (!port) return;
  event.waitUntil((async () => {
    try {
      if (event.data?.type === 'SAVE_OFFLINE') port.postMessage(await saveBundle());
      else if (event.data?.type === 'OFFLINE_STATUS') {
        const status = await (await caches.open(CACHE)).match(READY);
        port.postMessage(status ? await status.json() : {ready: false});
      }
    } catch (_) { port.postMessage({ready: false, error: true}); }
  })());
});
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || !url.href.startsWith(ROOT)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const key = new URL(url);
    key.search = '';
    key.hash = '';
    if (key.href === ROOT) key.pathname += 'index.html';
    const cached = await cache.match(key.href);
    if (request.mode !== 'navigate' && cached) return cached;
    try {
      const response = await fetch(request);
      if (response.ok) return response;
      return cached || response;
    } catch (_) {
      return cached || new Response('ยังไม่ได้บันทึกหน้านี้สำหรับออฟไลน์ กรุณาต่ออินเทอร์เน็ตแล้วบันทึกอีกครั้ง', {
        status: 503, headers: {'Content-Type': 'text/plain; charset=utf-8'}
      });
    }
  })());
});
