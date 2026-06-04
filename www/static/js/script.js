

let deferredPrompt = null;
let qrScanner = null;

if (!crypto.randomUUID) {
    crypto.randomUUID = function() {
        return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    };
}

const media = window.matchMedia("(prefers-color-scheme: dark)");

function applyTheme(e) {
    const root = document.documentElement;
    if (e.matches) {
        root.classList.remove("light");
    } else {
        root.classList.add("light");
    }
}

applyTheme(media);
media.addEventListener("change", applyTheme);


async function checkCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return { ok: false, error: "unsupported" };
    }

    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const hasCamera = devices.some(d => d.kind === "videoinput");

        if (!hasCamera) {
            return { ok: false, error: "no_camera" };
        }

        return { ok: true };

    } catch (err) {
        return { ok: false, error: err.name || "unknown" };
    }
}


function startQRScanner() {
    qrScanner = new Html5Qrcode("toga_qr_scanner");

    qrScanner.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: 250 },

        (decodedText) => {
            if (window.on_qr_scanned) {
                window.on_qr_scanned(decodedText);
            }
        }
    ).catch((err) => {
        console.error("QR start error:", err);

        if (window.on_qr_error) {
            window.on_qr_error(String(err));
        }
    });
}

function stopQRScanner() {

    if (!qrScanner) {
        return;
    }

    qrScanner.stop()
        .then(() => {
            qrScanner.clear();
            qrScanner = null;
        })
        .catch((err) => {
            console.warn("QR stop error:", err);

            try {
                qrScanner.clear();
            } catch (e) {}

            qrScanner = null;
        });
}

window.qr = {
    startQR: startQRScanner,
    stopQR: stopQRScanner,
    checkCamera: checkCamera
};

window.addEventListener("beforeinstallprompt", (e) => {
    deferredPrompt = e;
});

window.addEventListener("appinstalled", () => {
    console.log("PWA installed");
    localStorage.setItem("pwa_installed", "true");
});

function isFirefox() {
    return navigator.userAgent.toLowerCase().includes("firefox");
}

function isPWAInstalled() {
    return (
        isFirefox() ||
        window.matchMedia("(display-mode: standalone)").matches ||
        window.navigator.standalone === true ||
        document.referrer?.includes("android-app://") ||
        localStorage.getItem("pwa_installed") === "true"
    );
}

window.installPWA = async () => {
    if (!deferredPrompt) {
        console.log("No deferredPrompt");
        return false;
    }
    deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;

    if (choice.outcome === "accepted") {
        localStorage.setItem("pwa_installed", "true");
    }
    deferredPrompt = null;
    return choice.outcome === "accepted";
};


if ("serviceWorker" in navigator) {
    window.addEventListener("load", async () => {
        try {
            const reg = await navigator.serviceWorker.register("/service-worker.js");
            reg.onupdatefound = () => {
                console.log("SW update found");
            };
        } catch (err) {
            console.error("SW registration failed:", err);
        }
    });
}