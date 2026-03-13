from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
import app.services as services
import app.schemas as schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create")
def create_game(data: schemas.CreateGame, db: Session = Depends(get_db)):

    code = services.create_game(db, data.host_name, data.rounds)

    return {"room_code": code}


@router.post("/join")
def join_game(data: schemas.JoinGame, db: Session = Depends(get_db)):

    state = services.get_state(db, data.room_code)

    if not state:
        return {"error": "Room not found"}

    state["players"].append({
        "name": data.player_name,
        "total": 0,
        "points": 0,
        "busted": False,
        "done": False,
        "used_dice": [],
    })

    services.save_state(db, data.room_code, state)

    return {"status": "joined"}