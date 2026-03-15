from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
import app.models.stock as stock_model
import app.models.watchlist as wl_model

router = APIRouter()

@router.get("/", response_model=List[schemas.WatchlistDetail])
def get_watchlist(db: Session = Depends(get_db)):
    # Assuming user_id = 1 for this scaffold
    user_id = 1

    items = db.query(
        wl_model.Watchlist, stock_model.Stock
    ).join(
        stock_model.Stock, wl_model.Watchlist.symbol == stock_model.Stock.symbol
    ).filter(
        wl_model.Watchlist.user_id == user_id
    ).all()
    
    result = []
    for w, s in items:
        result.append({
            "id": w.id,
            "symbol": s.symbol,
            "name": s.name,
            "exchange": s.exchange,
            "added_at": w.added_at
        })
    return result
