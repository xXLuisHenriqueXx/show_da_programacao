import { useMemo } from "react";
import { Loader2 } from "lucide-react";

import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { SparklesText } from "@/components/ui/sparkles-text";
import {
  AnimatedSpan,
  Terminal,
  TypingAnimation,
} from "@/components/ui/terminal";

import { useHome } from "./_hooks/useHome";

function Home() {
  const { loading, onPressStart } = useHome();

  const renderButtonContent = useMemo(() => {
    if (loading) return <Loader2 className="animate-spin" />;
    return "{ COMEÇAR }";
  }, [loading]);

  return (
    <Container>
      <SparklesText>&#123; Show da Programação &#125;</SparklesText>

      <Terminal className="h-auto">
        <TypingAnimation className="text-primary/75" duration={5}>
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
        <TypingAnimation className="text-primary/75 text-wrap" duration={5}>
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
