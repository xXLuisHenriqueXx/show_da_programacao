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
  InputGroupInput,
} from "@/components/ui/input-group";
import { Separator } from "@/components/ui/separator";
import { useChat } from "@/hooks/useChat";
import { ArrowRight, X } from "lucide-react";
import { useEffect, useState, useRef } from "react";

interface IChatModalProps {
  uuid: string;
  show: boolean;
  setShow: (show: boolean) => void;
}

const ChatModal = ({ uuid, show, setShow }: IChatModalProps) => {
  const { messages, sendMessage, connected, streaming, connect, disconnect } =
    useChat(uuid);

  const [message, setMessage] = useState("");
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (show) connect();
    else disconnect();
  }, [show, uuid]);

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, streaming]);

  if (!show) return null;

  return (
    <Card className="absolute bottom-4 right-4 max-w-lg max-h-2/3">
      <CardHeader>
        <CardTitle>Tutor Artificial</CardTitle>
        <CardAction onClick={() => setShow(false)}>
          <X className="w-4 h-4" />
        </CardAction>
      </CardHeader>

      <CardContent className="flex flex-col gap-2 overflow-auto">
        {!connected && <p>Conectando...</p>}

        <div
          ref={chatRef}
          style={{
            flex: 1,
            height: 300,
            overflowY: "auto",
            padding: "8px",
            borderRadius: 8,
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          {messages.map((m) => (
            <Card
              key={m.id}
              className={`max-w-3/4 p-2 ${
                m.role === "user" ? "self-end" : "self-start border-0"
              } ${m.pending ? "bg-gray-700" : ""}`}
            >
              <CardContent>
                <p>{m.content}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>

      <CardFooter>
        <InputGroup>
          <InputGroupInput
            disabled={!connected}
            value={message}
            placeholder={streaming ? "Aguarde..." : "Digite sua mensagem..."}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage(message);
                setMessage("");
              }
            }}
          />

          <InputGroupButton className="p-2 mr-1" disabled={!connected}>
            <ArrowRight className="w-4 h-4" />
          </InputGroupButton>
        </InputGroup>
      </CardFooter>
    </Card>
  );
};

export default ChatModal;
