// FLUGEL — telefona "uygulama olarak yukle" icin gereken en sade service worker (onbellek yok, hep canli veri)
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", () => {});
