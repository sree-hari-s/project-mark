import { useEffect, useState } from "react";
import { getState } from "../api/api";
import { useParams } from "react-router-dom";

export default function Lobby() {

  const { room } = useParams();

  const [state, setState] = useState(null);

  useEffect(() => {

    const interval = setInterval(async () => {

      const res = await getState(room);
      setState(res.data);

    }, 2000);

    return () => clearInterval(interval);

  }, []);

  if (!state) return <div>Loading...</div>;

  return (
    <div>

      <h2>Room {room}</h2>

      <h3>Players</h3>

      {state.players.map(p => (
        <div key={p.name}>{p.name}</div>
      ))}

    </div>
  );
}