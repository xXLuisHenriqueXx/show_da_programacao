import { gameService, type IQuestion } from "@/services/Game.service";
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";

export const useQuestion = () => {
  const [question, setQuestion] = useState<IQuestion | null>(null);
  const [winner, setWinner] = useState<boolean>(false);
  const [showFinalModal, setShowFinalModal] = useState<boolean>(false);
  const [showChatModal, setShowChatModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const { uuid } = useParams();
  const navigate = useNavigate();

  const fetchQuestion = useCallback(async () => {
    setLoading(true);
    try {
      const { status, question } = await gameService.getNextQuestion(uuid!);

      if (status === 201) {
        setWinner(true);
        setShowFinalModal(true);
        return;
      }

      if (status < 200 || status > 300) {
        navigate("/");
        return;
      }

      setQuestion(question);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [uuid, navigate]);

  const sendAnswer = useCallback(
    async (option_index: number) => {
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

        if (!answer.correct) {
          setWinner(false);
          setShowFinalModal(true);
          return;
        }

        await fetchQuestion();
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    },
    [uuid, navigate, fetchQuestion]
  );

  useEffect(() => {
    fetchQuestion();
  }, [showFinalModal, fetchQuestion]);

  if (!uuid) navigate("/");

  const formatCurrency = (value: number) => {
    return value?.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  };

  return {
    uuid,
    question,
    winner,
    fetchQuestion,
    showFinalModal,
    showChatModal,
    loading,
    formatCurrency,
    sendAnswer,
    setShowFinalModal,
    setShowChatModal,
  };
};
