import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { Bot } from "lucide-react";

import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { SparklesText } from "@/components/ui/sparkles-text";
import { Terminal, TypingAnimation } from "@/components/ui/terminal";

import { gameService, type IQuestion } from "@/services/Game.service";
import Tutor from "@/assets/tutor.png";
import FinalModal from "./_components/FinalModal";
import ChatModal from "./_components/ChatModal";

const Question = () => {
  const [question, setQuestion] = useState<IQuestion | null>(null);
  const [winner, setWinner] = useState<boolean>(false);
  const [showFinalModal, setShowFinalModal] = useState<boolean>(false);
  const [showChatModal, setShowChatModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const { uuid } = useParams();
  const navigate = useNavigate();

  const sendAnswer = useCallback(async (option_index: number) => {
    setLoading(true);

    try {
      const { status, answer } = await gameService.answerQuestion(
        uuid!,
        option_index
      );

      if (status < 200 || status > 300) {
        navigate("/");
        return;
      }

      if (!answer?.correct) {
        setWinner(false);
        setShowFinalModal(true);
      }

      fetchQuestion();
    } catch (error) {
      alert(error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchQuestion = async () => {
    setLoading(true);

    try {
      const { status, question } = await gameService.getNextQuestion(uuid!);

      if (status < 200 || status > 300) navigate("/");

      if (status === 201) {
        console.log("entrou aqui");
        setWinner(true);
        setShowFinalModal(true);

        return;
      }

      setQuestion(question ?? null);
    } catch (error) {
      alert(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestion();
  }, [showFinalModal]);

  if (!uuid) navigate("/");

  const formatCurrency = (value: number) => {
    return value?.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  };

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
      />

      <ChatModal uuid={uuid!} show={showChatModal} setShow={setShowChatModal} />
    </Container>
  );
};

export default Question;
