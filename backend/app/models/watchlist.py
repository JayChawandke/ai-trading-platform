from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base
from datetime import datetime

class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    symbol = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
