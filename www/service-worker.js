
const CACHE_NAME = "btcz-wallet-v1.0.9";

self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (event) => {
    const url = event.request.url;
    if (url.includes("cloudflareinsights.com")) {
        return;
    }

    event.respondWith(
        fetch(event.request).catch((error) => {
            console.warn("SW fetch failed:", url, error);

            return new Response("", {
                status: 503,
                statusText: "Offline",
            });
        })
    );
});