import json
import random
import string

from sqlalchemy.orm import Session
from app.models import Game
from app.game_logic import create_state, new_player


def generate_code():

    chars = string.ascii_uppercase + string.digits

    return "".join(random.choices(chars, k=6))


def create_game(db: Session, host_name: str, rounds: int):

    room_code = generate_code()

    state = create_state(host_name, rounds)

    game = Game(
        room_code=room_code,
        state=json.dumps(state)
    )

    db.add(game)
    db.commit()

    return room_code


def get_state(db: Session, room_code: str):

    game = db.query(Game).filter(Game.room_code == room_code).first()

    if not game:
        return None

    return json.loads(game.state)


def save_state(db: Session, room_code: str, state):

    game = db.query(Game).filter(Game.room_code == room_code).first()

    game.state = json.dumps(state)

    db.commit()


def join_game(db: Session, room_code: str, player_name: str):

    state = get_state(db, room_code)

    if not state:
        return {"error": "Room not found"}

    state["players"].append(new_player(player_name))

    save_state(db, room_code, state)

    return {"status": "joined"}