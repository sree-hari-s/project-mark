from pydantic import BaseModel


class CreateGame(BaseModel):
    host_name: str
    rounds: int


class JoinGame(BaseModel):
    room_code: str
    player_name: str


class RollDice(BaseModel):
    room_code: str
    player_name: str
    sides: int


class EndTurn(BaseModel):
    room_code: str
    player_name: str