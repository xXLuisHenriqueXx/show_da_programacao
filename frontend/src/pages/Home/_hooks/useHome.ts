import { gameService } from "@/services/Game.service";
import confetti from "canvas-confetti";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router";

export const useHome = () => {
  const [loading, setLoading] = useState<boolean>(false);

  const navigate = useNavigate();

  const onPressStart = useCallback(async () => {
    setLoading(true);

    try {
      const { status, uuid } = await gameService.start();
      if (status !== 200) {
        setLoading(false);
        return;
      }

      const DURATION = 2500;
      const END = performance.now() + DURATION;
      const defaults = { startVelocity: 30, spread: 240, ticks: 50, zIndex: 0 };
      const randomInRange = (min: number, max: number) =>
        Math.random() * (max - min) + min;

      const interval = window.setInterval(() => {
        const timeLeft = END - performance.now();

        if (timeLeft <= 0) {
          return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / DURATION);

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
      }, DURATION);
    } catch (error) {
      console.error(error);
      setLoading(false);
      return;
    }
  }, [navigate]);

  return {
    loading,
    onPressStart,
  };
};
