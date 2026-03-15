from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db, engine, Base
from ..models.trade import Trade as TradeModel
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(tags=["trade"])

class OrderRequest(BaseModel):
    symbol: str
    side: str # BUY or SELL
    quantity: float
    price: float

@router.post("/order")
def place_order(order: OrderRequest, db: Session = Depends(get_db)):
    new_trade = TradeModel(
        user_id=1,
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        price=order.price,
        timestamp=datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    return new_trade

@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    trades = db.query(TradeModel).filter(TradeModel.user_id == 1).all()
    
    holdings = {}
    for t in trades:
        sym = t.symbol
        if sym not in holdings:
            holdings[sym] = {"symbol": sym, "quantity": 0, "avg_price": 0, "total_cost": 0}
        
        if t.side == "BUY":
            holdings[sym]["quantity"] += t.quantity
            holdings[sym]["total_cost"] += (t.quantity * t.price)
        else:
            holdings[sym]["quantity"] -= t.quantity
            holdings[sym]["total_cost"] -= (t.quantity * t.price)
            
    for sym in holdings:
        if holdings[sym]["quantity"] > 0:
            holdings[sym]["avg_price"] = holdings[sym]["total_cost"] / holdings[sym]["quantity"]
        else:
            holdings[sym]["avg_price"] = 0
            
    return list(holdings.values())
