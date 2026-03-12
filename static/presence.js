const presenceChip = document.getElementById("presence-chip");
const presenceState = document.getElementById("presence-state");
const presenceDetail = document.getElementById("presence-detail");
const PRESENCE_CLIENT_KEY = "local-image-drop-client-id";
const presencePage = window.APP_CONFIG?.presencePage || "unknown";
const heartbeatIntervalMs = (window.APP_CONFIG?.presenceHeartbeatSeconds || 5) * 1000;

const setPresenceFallback = (message) => {
  if (!presenceChip || !presenceState || !presenceDetail) {
    return;
  }

  presenceChip.classList.remove("connected");
  presenceChip.classList.add("disconnected");
  presenceState.textContent = "Status unavailable";
  presenceDetail.textContent = message;
};

const getClientId = () => {
  try {
    const existingClientId = window.localStorage.getItem(PRESENCE_CLIENT_KEY);
    if (existingClientId) {
      return existingClientId;
    }
  } catch (_error) {
    // Ignore localStorage failures and use in-memory fallback.
  }

  const newClientId =
    window.crypto?.randomUUID?.() ||
    `client-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
  try {
    window.localStorage.setItem(PRESENCE_CLIENT_KEY, newClientId);
  } catch (_error) {
    // Ignore localStorage failures and continue with current id.
  }
  return newClientId;
};

const formatPeerList = (peers) =>
  peers
    .map((peer) => `${peer.label} (${peer.host})`)
    .join(" | ");

const renderPresence = (payload) => {
  if (!presenceChip || !presenceState || !presenceDetail) {
    return;
  }

  const peerTypeLabel = payload.peer_role === "phone" ? "phone" : "computer";
  if (payload.peer_connected) {
    presenceChip.classList.remove("disconnected");
    presenceChip.classList.add("connected");
    presenceState.textContent = "Connected";
    presenceDetail.textContent = formatPeerList(payload.peers);
    return;
  }

  presenceChip.classList.remove("connected");
  presenceChip.classList.add("disconnected");
  presenceState.textContent = "Not connected";
  presenceDetail.textContent = `No active ${peerTypeLabel} connection.`;
};

const buildPresencePayload = (clientId) =>
  JSON.stringify({
    client_id: clientId,
    page: presencePage,
  });

const startPresenceMonitoring = () => {
  if (!presenceChip) {
    return;
  }

  const clientId = getClientId();

  const sendHeartbeat = async () => {
    try {
      const response = await fetch("/presence/heartbeat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: buildPresencePayload(clientId),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Presence heartbeat failed.");
      }
      renderPresence(payload);
    } catch (error) {
      setPresenceFallback(error.message || "Could not update connection status.");
    }
  };

  const sendBeaconHeartbeat = () => {
    if (!navigator.sendBeacon) {
      return;
    }
    const heartbeatBlob = new Blob([buildPresencePayload(clientId)], {
      type: "application/json",
    });
    navigator.sendBeacon("/presence/heartbeat", heartbeatBlob);
  };

  sendHeartbeat();
  window.setInterval(sendHeartbeat, heartbeatIntervalMs);

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      sendBeaconHeartbeat();
      return;
    }
    sendHeartbeat();
  });
  window.addEventListener("beforeunload", sendBeaconHeartbeat);
};

startPresenceMonitoring();
