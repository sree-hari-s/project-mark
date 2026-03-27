import { useEffect, useState } from "react";
import { getState, rollDice, endTurn } from "../api/api";
import { useParams, useLocation } from "react-router-dom";

export default function Game() {
  const { room } = useParams();
  const { state } = useLocation();

  const player = state.player;

  const [game, setGame] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await getState(room);
      setGame(res.data);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  if (!game) return <div>Loading...</div>;

  return (
    <div>
      <h2>Mark: {game.mark}</h2>

      <button onClick={() => rollDice(room, player, 6)}>Roll d6</button>

      <button onClick={() => rollDice(room, player, 12)}>Roll d12</button>

      <button onClick={() => rollDice(room, player, 20)}>Roll d20</button>

      <button onClick={() => endTurn(room, player)}>End Turn</button>
    </div>
  );
}
