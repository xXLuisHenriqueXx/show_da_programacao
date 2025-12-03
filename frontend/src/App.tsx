import { Route, Routes } from "react-router";
import Home from "./pages/Home";
import Question from "./pages/Question";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/question/:uuid" element={<Question />} />
    </Routes>
  );
}

export default App;
