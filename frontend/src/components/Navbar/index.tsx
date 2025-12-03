import { useCallback, useEffect, useState } from "react";
import { AnimatedGradientText } from "../ui/animated-gradient-text";
import { Moon, Sun } from "lucide-react";
import { Button } from "../ui/button";
import { Link } from "react-router";

function Navbar() {
  const [isDark, setIsDarkTheme] = useState(
    document.body.classList.contains("dark")
  );

  const toggleTheme = useCallback(() => {
    document.body.classList.toggle("dark");
  }, []);

  useEffect(() => {
    const html = document.body;

    const observer = new MutationObserver(() => {
      setIsDarkTheme(html.classList.contains("dark"));
    });

    observer.observe(html, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4">
      <Link to="/">
        <AnimatedGradientText className="flex flex-row items-center font-bold">
          <span className="mr-2">🚀</span>
          &#123; Show da Programação &#125;
        </AnimatedGradientText>
      </Link>

      <Button variant={"outline"} onClick={toggleTheme}>
        {isDark ? <Moon /> : <Sun />}
      </Button>
    </header>
  );
}

export default Navbar;
