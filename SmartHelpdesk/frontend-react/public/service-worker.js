const CACHE_NAME = 'helpdesk-react-v1';
const CORE = [
  '/',
  '/manifest.webmanifest'
];

// Install
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(CORE))
  );
});

// Activate (clean old)
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
});

// Fetch strategy: Network-first for API, cache-first for static
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/tickets') || url.pathname.startsWith('/chat')) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }
  event.respondWith(
    caches.match(event.request).then(res => res || fetch(event.request))
  );
});