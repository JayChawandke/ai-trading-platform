from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WatchlistDetail(BaseModel):
    id: int
    symbol: str
    name: Optional[str]
    exchange: Optional[str]
    added_at: datetime

    class Config:
        from_attributes = True
