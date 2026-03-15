from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String)
    exchange = Column(String, default="NSE")
    sector = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
