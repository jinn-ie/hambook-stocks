from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.dependencies.db import get_db_session
from app.models.user_models import User
from app.models.mystocks_models import MyStocks
from app.models.parameter_models import stock_to_buy

router = APIRouter(
    prefix = '/trade'
)

class buyResp(): #응답모델
    login_id: str
    access_token: str
    stock_code : int
    quantity: int

@router.post("/buy") #req: 수량, 금액, 주식 코드, 
def buy_stock(req: stock_to_buy, db: Session = Depends(get_db_session), authorization: str =Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="로그인하셔야 합니다.")
    
    token = authorization.split(" ")[1]
    user = db.query(User).filter(User.access_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail= "유효하지 않은 토큰입니다")
    
    # 토큰 인증은 끝
    # 2. 돈이 있는지 없는지 확인하자자
    total_price = req.stock_price * req.quantity
    if user.balance < total_price:
        raise HTTPException(status_code=400, detail="잔액이 부족합니다.")
    
    # 돈이 있으면 User의 산 가격만큼 돈을 줄이고

    change = user.balance - total_price
    db.query(User).filter(User.id == user.id).update({"balance": change})
    #잔돈으로 새로 업데이트한 후에

    existing_stock = db.query(MyStocks).filter(MyStocks.stock_code == req.stock_code).first()

    if existing_stock:
        db.query(MyStocks).filter(MyStocks.stock_code == req.stock_code).update({"quantity": MyStocks.quantity + req.quantity})
        
        new_avg_price = (total_price + existing_stock.avg_price*existing_stock.quantity) / (req.quantity + existing_stock.quantity)
        db.query(MyStocks).filter(MyStocks.stock_code == req.stock_code).update({"avg_price": new_avg_price})
        db.commit()
        #DB에 주식을 추가해준다

    else:
        new_stock = MyStocks(
            login_id = user.id,
            stock_code=req.stock_code,
            quantity=req.quantity,
            access_token= user.access_token,
            avg_price = req.stock_price
        )
        db.add(new_stock)
    db.commit()
    
    return {"msg": "구매 완료"}
