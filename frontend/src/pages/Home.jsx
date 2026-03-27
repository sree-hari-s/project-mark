import { useState } from "react";
import { createGame, joinGame } from "../api/api";
import { useNavigate } from "react-router-dom";

export default function Home() {

  const [name, setName] = useState("");
  const [room, setRoom] = useState("");

  const navigate = useNavigate();

  const handleCreate = async () => {

    const res = await createGame(name, 3);

    navigate(`/lobby/${res.data.room_code}`, {
      state: { player: name }
    });
  };

  const handleJoin = async () => {

    await joinGame(room, name);

    navigate(`/lobby/${room}`, {
      state: { player: name }
    });
  };

  return (
    <div>

      <h1>Project Mark</h1>

      <input
        placeholder="Your Name"
        onChange={(e) => setName(e.target.value)}
      />

      <button onClick={handleCreate}>
        Create Game
      </button>

      <hr />

      <input
        placeholder="Room Code"
        onChange={(e) => setRoom(e.target.value)}
      />

      <button onClick={handleJoin}>
        Join Game
      </button>

    </div>
  );
}