const CACHE_NAME = 'guitar-tab-cache-v8';

// Only cache stable assets — NOT HTML pages
const urlsToCache = [
  '/manifest.json',
  '/icon.svg'
];

const NETWORK_FIRST_PATHS = ['/v2', '/manual'];
const NETWORK_FIRST_PREFIXES = ['/api/', '/static/v2-project.js', '/static/tab-format.js'];

function isNetworkFirst(url) {
  const path = new URL(url).pathname;
  if (NETWORK_FIRST_PATHS.includes(path)) return true;
  return NETWORK_FIRST_PREFIXES.some(prefix => path.startsWith(prefix) || path.endsWith('v2-project.js'));
}

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache).catch(() => {}))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) return caches.delete(cacheName);
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  // Let the browser handle the root redirect natively to avoid service worker redirect bugs!
  const url = event.request.url;
  const path = new URL(url).pathname;
  if (path === '/') return;
  if (isNetworkFirst(url)) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && (response.status === 200 || response.type === 'opaqueredirect' || response.status === 302 || response.status === 307 || response.status === 304)) return response;
          return caches.match(event.request);
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (!response || response.status !== 200 || response.type === 'opaque') {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      });
    })
  );
});
