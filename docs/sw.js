const CACHE_NAME = 'breakinvaders-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './favicon.png',
  './manifest.json',
  './img/bg.png',
  './img/spaceship.png',
  './img/bullet.png',
  './img/alien1.png',
  './img/alien2.png',
  './img/alien3.png',
  './img/alien4.png',
  './img/alien5.png',
  './img/boss.png',
  './img/exp1.png',
  './img/exp2.png',
  './img/exp3.png',
  './img/exp4.png',
  './img/exp5.png',
  './img/explosion.wav',
  './img/explosion2.wav',
  './img/laser.wav',
  './img/bw/spaceship_bw_cleaned_final.png',
  './img/bw/bullet_bw_cleaned_final.png',
  './img/bw/alien1_bw_cleaned_final.png',
  './img/bw/alien2_bw_cleaned_final.png',
  './img/bw/alien3_bw_cleaned_final.png',
  './img/bw/alien4_bw_cleaned_final.png',
  './img/bw/alien5_bw_cleaned_final.png',
  './img/bw/boss_bw.png',
  './img/bw/exp1_bw_cleaned_final.png',
  './img/bw/exp2_bw_cleaned_final.png',
  './img/bw/exp3_bw_cleaned_final.png',
  './img/bw/exp4_bw_cleaned_final.png',
  './img/bw/exp5_bw_cleaned_final.png'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        // Cache assets one by one to handle individual failures
        return Promise.allSettled(
          ASSETS_TO_CACHE.map(url => 
            fetch(url)
              .then(response => {
                if (!response.ok) {
                  throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
                }
                return cache.put(url, response);
              })
              .catch(error => {
                console.warn(`Failed to cache ${url}:`, error);
                // Continue with other assets even if one fails
                return Promise.resolve();
              })
          )
        );
      })
      .catch((error) => {
        console.error('Cache initialization failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if found
        if (response) {
          return response;
        }
        
        // Clone the request because it can only be used once
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest)
          .then((response) => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone the response because it can only be used once
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              })
              .catch((error) => {
                console.error('Cache put failed:', error);
              });
              
            return response;
          })
          .catch((error) => {
            console.error('Fetch failed:', error);
            // Return a fallback response if fetch fails
            return new Response('Network error occurred', {
              status: 408,
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
}); 