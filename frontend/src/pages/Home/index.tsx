import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import confetti from "canvas-confetti";
import { Loader2 } from "lucide-react";

import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { SparklesText } from "@/components/ui/sparkles-text";
import {
  AnimatedSpan,
  Terminal,
  TypingAnimation,
} from "@/components/ui/terminal";

import { gameService } from "@/services/Game.service";

function Home() {
  const [loading, setLoading] = useState<boolean>(false);

  const navigate = useNavigate();

  const onPressStart = useCallback(async () => {
    setLoading(true);

    try {
      const duration = 2.5 * 1000;
      const animationEnd = Date.now() + duration;

      const { status, uuid } = await gameService.start();
      if (status !== 200) return;

      const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };
      const randomInRange = (min: number, max: number) =>
        Math.random() * (max - min) + min;

      const interval = window.setInterval(() => {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
          return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);

        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
        });
        confetti({
          ...defaults,
          particleCount,
          origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
        });
      }, 250);

      setTimeout(() => {
        navigate(`/question/${uuid}`);
      }, duration);
    } catch (error) {
      alert(error);
    } finally {
      setTimeout(() => {
        setLoading(false);
      }, 2500);
    }
  }, [navigate]);

  const renderButtonContent = useMemo(() => {
    if (loading) return <Loader2 className="animate-spin" />;
    return "{ COMEÇAR }";
  }, [loading]);

  return (
    <Container>
      <SparklesText>&#123; Show da Programação &#125;</SparklesText>

      <Terminal className="h-auto">
        <TypingAnimation className="text-primary/75">
          PS C:\System32&gt; Se desafie respondendo perguntas sobre:
        </TypingAnimation>
        <AnimatedSpan className="text-green-300">
          echo "Design Patterns"
        </AnimatedSpan>
        <AnimatedSpan className="text-green-300">
          echo "Code Smells"
        </AnimatedSpan>
        <AnimatedSpan className="text-green-300">
          echo "Refatoração"
        </AnimatedSpan>
        <AnimatedSpan className="text-green-300">
          echo "Arquitetura"
        </AnimatedSpan>
        <TypingAnimation className="text-primary/75 text-wrap">
          PS C:\System32&gt; Afim de melhorar a qualidade do seu código e
          aprendizado!
        </TypingAnimation>

        <br />

        <Button onClick={onPressStart} disabled={loading}>
          {renderButtonContent}
        </Button>
      </Terminal>
    </Container>
  );
}

export default Home;
