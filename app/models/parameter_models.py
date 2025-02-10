from pydantic import BaseModel
from app.models.user_models import User

class AuthSigninReq(BaseModel):
    login_id: str
    pwd: str

class AuthSignupReq(BaseModel):
    login_id: str
    pwd: str
    name: str

class AuthResp(BaseModel):
    message: str
    user: User
    # access_token: str | None = None