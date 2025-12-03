import type { ReactNode } from "react";

import Navbar from "../Navbar";
import { FlickeringGrid } from "../ui/flickering-grid";
import { SmoothCursor } from "../ui/smooth-cursor";
import { SpinningText } from "../ui/spinning-text";

import UFSM from "@/assets/ufsm.png";

interface IContainerProps {
  children: ReactNode;
}

const Container = ({ children }: IContainerProps) => {
  return (
    <main className="relative flex flex-col items-center justify-center gap-8 w-full h-dvh">
      <SmoothCursor />
      <Navbar />
      <FlickeringGrid
        className="absolute top-0 left-0 right-0 w-full h-full pointer-events-none"
        color="rgb(50, 50, 50)"
      />

      {children}

      <div className="absolute bottom-24 left-24 flex items-center justify-center">
        <div className="relative">
          <SpinningText className="absolute top-0 left-0 right-0 bottom-0">
            Análise e Projeto •
          </SpinningText>
          <img className="w-12" src={UFSM} alt="UFSM" />
        </div>
      </div>
    </main>
  );
};

export default Container;
