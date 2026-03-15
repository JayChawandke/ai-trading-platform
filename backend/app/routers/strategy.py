
from fastapi import APIRouter
from ..services.strategy_engine import moving_average_strategy

router = APIRouter(prefix="/strategy")

@router.get("/ma/{symbol}")
def ma_strategy(symbol:str):
    signal = moving_average_strategy(symbol)
    return {"symbol":symbol,"signal":signal}
