from sqlalchemy import Column, String, Text
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    room_code = Column(String, primary_key=True, index=True)
    state = Column(Text)