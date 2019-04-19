console.log('Hello from sw.js');

importScripts('https://cdn.jsdelivr.net/npm/workbox-cdn/workbox/workbox-sw.js');
workbox.setConfig({
  modulePathPrefix: 'https://cdn.jsdelivr.net/npm/workbox-cdn/workbox/'
});


if (workbox) {
  console.log("Yay! Workbox is loaded");

  workbox.precaching.precacheAndRoute([]);

  workbox.routing.registerRoute(
    /\.(?:js|css)$/,
    workbox.strategies.staleWhileRevalidate({
      cacheName: 'static-resources',
    }),
  );

  workbox.routing.registerRoute(
    /\.(?:png|gif|jpg|jpeg|svg|webm|ogg|mp4)$/,
    workbox.strategies.cacheFirst({
      cacheName: 'images',
      plugins: [
        new workbox.expiration.Plugin({
          maxEntries: 60,
          maxAgeSeconds: 30 * 24 * 60 * 60,
        }),
      ],
    }),
  );

} else {
  console.log("Boo! Workbox didn't load");
}
