window.AEG_WEB_CONFIG = {
    // local: 连接本机后端
    // default: 连接默认后端地址
    backendMode: "local",
    backends: {
        local: "http://127.0.0.1:5000",
        default: "http://127.0.0.1:5000",
    },
};

(function applyWebConfig() {
    const config = window.AEG_WEB_CONFIG || {};
    const backends = config.backends || {};
    const mode = config.backendMode || "local";
    const selectedBackend = backends[mode] || backends.local || "http://127.0.0.1:5000";
    window.AEG_API_BASE = String(selectedBackend).replace(/\/+$/, "");
})();
