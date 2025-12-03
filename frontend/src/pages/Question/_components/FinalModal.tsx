import { Button } from "@/components/ui/button";
import {
  AnimatedSpan,
  Terminal,
  TypingAnimation,
} from "@/components/ui/terminal";
import { gameService } from "@/services/Game.service";
import { useMemo, useState } from "react";

interface IFinalModalProps {
  winner: boolean;
  uuid: string;
  show: boolean;
  setShow: (show: boolean) => void;
}

const FinalModal = ({ winner, uuid, show, setShow }: IFinalModalProps) => {
  const [loading, setLoading] = useState<boolean>(false);

  const onPressReset = async () => {
    setLoading(true);

    try {
      const { status } = await gameService.reset(uuid!);

      if (status !== 200) return;

      setShow(false);
    } catch (error) {
      alert(error);
    } finally {
      setLoading(false);
    }
  };

  const title = winner
    ? "{ Parabéns, você ganhou! }"
    : "{ Que pena, você perdeu! }";

  const renderDescription = useMemo(() => {
    if (winner) {
      return (
        <>
          <AnimatedSpan className="text-green-300 text-wrap">
            echo "Você mandou muito bem"
          </AnimatedSpan>
          <AnimatedSpan className="text-green-300 text-wrap">
            echo "Escolha sua próxima ação nos botões abaixo"
          </AnimatedSpan>
        </>
      );
    } else {
      return (
        <>
          <AnimatedSpan className="text-green-300 text-wrap">
            echo "Mas não se desanime, você pode tentar novamente"
          </AnimatedSpan>
          <AnimatedSpan className="text-green-300 text-wrap">
            echo "Se vocês tiver alguma dúvida, sinta-se livre para perguntar ao
            nosso tutor"
          </AnimatedSpan>
          <AnimatedSpan className="text-green-300 text-wrap">
            echo "Escolha sua próxima ação nos botões abaixo"
          </AnimatedSpan>
        </>
      );
    }
  }, [winner]);

  return (
    show && (
      <div className="fixed top-0 left-0 right-0 bottom-0 flex items-center justify-center bg-black/75 bg-opacity-50 z-50">
        <Terminal className="h-auto">
          <TypingAnimation className="text-2xl font-bold text-center">
            {title}
          </TypingAnimation>

          <AnimatedSpan> </AnimatedSpan>
          <AnimatedSpan> </AnimatedSpan>
          <AnimatedSpan> </AnimatedSpan>

          {renderDescription}

          <br />

          <div className="flex flex-col gap-2">
            <Button onClick={onPressReset} disabled={loading}>
              Recomeçar jogo
            </Button>

            <Button disabled={loading}>Retornar para tela inicial</Button>
          </div>
        </Terminal>
      </div>
    )
  );
};

export default FinalModal;
