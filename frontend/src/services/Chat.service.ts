type CallbackFn = (data: any) => void;

interface MessageBase {
  client_message: string;
}

export function createChatService() {
  let socketRef: WebSocket | null = null;
  let isConnected = false;
  let reconnectAttempts = 0;
  let timeout: any | null = null;
  let chatId: string | null = null;
  const maxReconnectAttempts = 5;
  const callbacks: Record<string, CallbackFn[]> = {};
  let pendingMessages: MessageBase[] = [];

  function connect(newChatId: string) {
    if (socketRef) {
      console.log("[WS] Already connecting or connected");
      return;
    }

    chatId = newChatId;
    const url = `ws://localhost:8000/ws/chat/${chatId}`;

    console.log("[WS] Connecting to:", url);
    socketRef = new WebSocket(url);

    socketRef.onopen = () => {
      console.log("[WS] Connected");
      isConnected = true;
      reconnectAttempts = 0;

      executeCallback("connect", null);
      flushPending();
    };

    socketRef.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("[WS] Incoming:", data);

        if (!data.type) {
          console.warn("[WS] Message without type, ignoring.");
          return;
        }

        executeCallback(data.type, data);
      } catch (err) {
        console.error("[WS] Failed to parse message", err);
      }
    };

    socketRef.onerror = (e) => {
      console.error("[WS] Error:", e);
      executeCallback("error", e);
    };

    socketRef.onclose = () => {
      console.log("[WS] Closed");
      isConnected = false;
      socketRef = null;

      if (reconnectAttempts < maxReconnectAttempts && chatId) {
        const delay = Math.min(1000 * 2 ** reconnectAttempts, 30000);
        reconnectAttempts++;

        console.log(`[WS] Reconnecting attempt ${reconnectAttempts}`);

        timeout = setTimeout(() => connect(chatId!), delay);
      } else {
        executeCallback("close", null);
      }
    };
  }

  function disconnect() {
    console.log("[WS] Manual disconnect");

    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }

    if (socketRef) {
      socketRef.onopen = null;
      socketRef.onmessage = null;
      socketRef.onerror = null;
      socketRef.onclose = null;
      socketRef.close();
      socketRef = null;
    }

    isConnected = false;
    reconnectAttempts = 0;
    pendingMessages = [];
    chatId = null;
  }

  function sendMessage(text: string): boolean {
    const payload = { client_message: text };

    if (socketRef?.readyState === WebSocket.OPEN) {
      socketRef.send(JSON.stringify(payload));
      return true;
    }

    pendingMessages.push(payload);
    return false;
  }

  function flushPending() {
    if (!pendingMessages.length) return;

    pendingMessages.forEach((msg) => socketRef?.send(JSON.stringify(msg)));

    pendingMessages = [];
  }

  function addCallbacks(messageType: string, callback: CallbackFn) {
    if (!callbacks[messageType]) callbacks[messageType] = [];
    callbacks[messageType].push(callback);
  }

  function removeCallbacks(messageType: string, callback: CallbackFn) {
    if (!callbacks[messageType]) return;
    callbacks[messageType] = callbacks[messageType].filter(
      (cb) => cb !== callback
    );
  }

  function executeCallback(messageType: string, data: any) {
    const list = callbacks[messageType];
    if (!list) return;
    list.forEach((cb) => cb(data));
  }

  return {
    connect,
    disconnect,
    sendMessage,
    addCallbacks,
    removeCallbacks,
    isConnected: () => isConnected,
  };
}
