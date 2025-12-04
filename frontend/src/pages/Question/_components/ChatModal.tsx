import { useEffect, useState, useRef } from "react";
import { ArrowRight, X } from "lucide-react";
import {
  Card,
  CardAction,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  InputGroup,
  InputGroupButton,
  InputGroupTextarea,
} from "@/components/ui/input-group";

import { useChat } from "@/hooks/useChat";
import { TypingIndicator } from "./TypingIndicator";

interface IChatModalProps {
  uuid: string;
  show: boolean;
  setShow: (show: boolean) => void;
}

const ChatModal = ({ uuid, show, setShow }: IChatModalProps) => {
  const { messages, sendMessage, connected, connect, disconnect, typing } =
    useChat(uuid);

  const [message, setMessage] = useState("");
  const chatRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (show) connect();
    return () => disconnect();
  }, [show, uuid]);

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  if (!show) return null;

  const handleSend = () => {
    if (!message.trim()) return;
    sendMessage(message);
    setMessage("");
  };

  return (
    <Card className="absolute bottom-4 right-4 w-lg max-h-[70vh] flex flex-col">
      <CardHeader>
        <CardTitle>Tutor Artificial</CardTitle>
        <CardAction onClick={() => setShow(false)}>
          <X className="w-4 h-4" />
        </CardAction>
      </CardHeader>

      <CardContent className="flex-1 overflow-auto">
        {!connected && (
          <p className="text-sm text-muted-foreground">Conectando...</p>
        )}

        <div
          ref={chatRef}
          className="flex flex-col gap-2 overflow-y-auto pr-1 h-full"
        >
          {messages.map((m) => (
            <Card
              key={m.id}
              className={`max-w-3/4 p-2 ${
                m.role === "user"
                  ? "self-end"
                  : "self-start border-0 bg-muted/20"
              }`}
            >
              <CardContent>
                <p>{m.content}</p>
              </CardContent>
            </Card>
          ))}

          {typing && <TypingIndicator />}
        </div>
      </CardContent>

      <CardFooter>
        <InputGroup>
          <InputGroupTextarea
            disabled={!connected || typing}
            value={message}
            placeholder={
              !connected || typing ? "Aguarde..." : "Digite sua mensagem..."
            }
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            rows={2}
          />

          <InputGroupButton
            className="p-2 mr-1"
            disabled={!connected || typing}
            onClick={handleSend}
          >
            <ArrowRight className="w-4 h-4" />
          </InputGroupButton>
        </InputGroup>
      </CardFooter>
    </Card>
  );
};

export default ChatModal;
