import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000"
});

export const createGame = (host, rounds) =>
  API.post("/create", { host_name: host, rounds });

export const joinGame = (room, player) =>
  API.post("/join", { room_code: room, player_name: player });

export const getState = (room) =>
  API.get(`/state/${room}`);

export const rollDice = (room, player, sides) =>
  API.post("/roll", {
    room_code: room,
    player_name: player,
    sides: sides
  });

export const endTurn = (room, player) =>
  API.post("/end-turn", {
    room_code: room,
    player_name: player
  });