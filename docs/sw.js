/* Send by GroupChatOn: keeps the app's own files on the device so it opens fast and installs as an app.
   Pages: network first (always the newest), falling back to the saved copy. Files never pass through here:
   transfers go device to device. */
var VERSION = '3e2b1de0a5';
var CACHE = 'gco-send-' + VERSION;
var FILES = ["/", "/manifest.webmanifest", "/brand/favicon-192.png", "/brand/favicon-512.png", "/brand/logo-light.png", "/brand/logo-dark.png", "/brand/mark.svg", "/assets/send.css?v=1faa3d3b", "/assets/send.js?v=75338177", "/assets/site.js?v=947b4fdc", "/assets/theme.js?v=c96dea8f"];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('gco-send-') === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return;
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).then(function (res) {
      var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(r, copy); }); return res;
    }).catch(function () { return caches.match(r).then(function (m) { return m || caches.match('/'); }); }));
    return;
  }
  e.respondWith(caches.match(r).then(function (m) { return m || fetch(r); }));
});
