import "../../../index.css";

export const TypingIndicator = () => {
  return (
    <div className="flex gap-1 items-center p-4 bg-muted/50 rounded-lg w-16">
      <span className="w-2 h-2 rounded-full bg-foreground animate-typing delay-300"></span>
      <span className="w-2 h-2 rounded-full bg-foreground animate-typing delay-150"></span>
      <span className="w-2 h-2 rounded-full bg-foreground animate-typing delay-0"></span>
    </div>
  );
};
