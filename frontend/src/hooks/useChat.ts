import { createChatService } from "@/services/Chat.service";
import { useCallback, useRef, useState } from "react";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
}

export function useChat(uuid?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState<boolean>(false);
  const [connected, setConnected] = useState<boolean>(false);
  const [typing, setTyping] = useState<boolean>(false);

  const socketRef = useRef<ReturnType<typeof createChatService> | null>(null);

  const connect = useCallback(() => {
    if (!uuid) return;
    if (!socketRef.current) socketRef.current = createChatService();

    const ws = socketRef.current;

    ws.addCallbacks("connect", () => setConnected(true));

    ws.addCallbacks("history", (d: any) => {
      const parsed = d.content.map((msg: any, i: number) => ({
        id: `history-${i}`,
        role: msg.role,
        content: msg.content,
      }));
      setMessages(parsed);
    });

    ws.addCallbacks("response_stream", (d: any) => {
      setStreaming(true);
      setMessages((prev) => {
        const last = prev[prev.length - 1];

        // Se última msg já é assistant em stream → concatena
        if (last && last.pending) {
          return [
            ...prev.slice(0, -1),
            { ...last, content: last.content + d.response_stream },
          ];
        }

        // Se ainda não existe mensagem em stream → cria uma pendente
        return [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: d.response_stream,
            pending: true,
          },
        ];
      });
    });

    ws.addCallbacks("full_text", (d: any) => {
      setStreaming(false);
      setTyping(false);
      setMessages((prev) => {
        const last = prev[prev.length - 1];

        // substitui mensagem pendente pelo texto final
        if (last?.pending) {
          return [
            ...prev.slice(0, -1),
            {
              ...last,
              content: d.content,
              pending: false,
            },
          ];
        }

        // fallback
        return [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: d.content,
          },
        ];
      });
    });

    ws.addCallbacks("control", (d: any) => {
      if (d.content === "[DONE]") {
        setStreaming(false);
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.pending) {
            return [...prev.slice(0, -1), { ...last, pending: false }];
          }
          return prev;
        });
      }
    });

    ws.addCallbacks("error", (d: any) => console.error("WS ERROR:", d));

    ws.connect(uuid);
  }, [uuid]);

  const disconnect = useCallback(() => {
    socketRef.current?.disconnect();
    setConnected(false);
  }, []);

  const sendMessage = useCallback((text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setTyping(true);

    // adiciona msg do user local antes de enviar
    setMessages((m) => [
      ...m,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
      },
    ]);

    socketRef.current?.sendMessage(trimmed);
  }, []);

  return {
    messages,
    sendMessage,
    connected,
    streaming,
    connect,
    disconnect,
    typing,
  };
}
