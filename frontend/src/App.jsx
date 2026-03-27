import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Lobby from "./pages/Lobby";
import Game from "./pages/Game";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Home />} />
        <Route path="/lobby/:room" element={<Lobby />} />
        <Route path="/game/:room" element={<Game />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;