import { useMemo } from "react";
import { Bot } from "lucide-react";

import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { SparklesText } from "@/components/ui/sparkles-text";
import { Terminal, TypingAnimation } from "@/components/ui/terminal";

import Tutor from "@/assets/tutor.png";
import FinalModal from "./_components/FinalModal";
import ChatModal from "./_components/ChatModal";
import { useQuestion } from "./_hooks/useQuestion";

const Question = () => {
  const {
    question,
    winner,
    loading,
    fetchQuestion,
    sendAnswer,
    formatCurrency,
    setShowChatModal,
    setShowFinalModal,
    uuid,
    showChatModal,
    showFinalModal,
  } = useQuestion();

  const title = useMemo(() => {
    if (question) return `PS C:\System32> ${question.text}`;

    return "PS C:System32> Buscando pergunta...";
  }, [question]);

  const value = useMemo(() => {
    if (question) return `{ ${formatCurrency(question.prize)} }`;

    return "R$ 0,00";
  }, [question]);

  return (
    <Container>
      <SparklesText>{value}</SparklesText>

      <Terminal className="h-auto">
        <TypingAnimation>{title}</TypingAnimation>

        <br />

        <div className="grid grid-cols-2 grid-rows-2 gap-2 w-full">
          {question?.options?.map((option, index) => (
            <Button
              key={option}
              disabled={loading}
              onClick={() => sendAnswer(index)}
            >
              {`{ ${option} }`}
            </Button>
          ))}
        </div>
      </Terminal>

      <div
        className="absolute bottom-4 right-4 flex flex-col items-center max-w-xl hover:scale-110 transition-all duration-300"
        onClick={() => setShowChatModal(true)}
      >
        <img className="w-24 -mb-4" src={Tutor} alt="Imagem do tutor" />
        <Button className="w-full">
          <Bot /> {"{ Pedir ajuda }"}
        </Button>
      </div>

      <FinalModal
        winner={winner}
        uuid={uuid!}
        show={showFinalModal}
        setShow={setShowFinalModal}
        fetchQuestion={fetchQuestion}
      />

      <ChatModal uuid={uuid!} show={showChatModal} setShow={setShowChatModal} />
    </Container>
  );
};

export default Question;
