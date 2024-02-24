from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Union
from pydantic import BaseModel
from jose import JWTError, jwt

from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .config import get_config

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conf_vars = get_config()
secret_key = conf_vars.jwt_secret_key
jwt_expire_minutes = conf_vars.jwt_expire_minutes


class Token(BaseModel):
    token: str
    type: str


class TokenData(BaseModel):
    user_id: Union[int, None] = None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")

        if authorization:
            scheme, _, credentials = authorization.partition(" ")
            if scheme in ["Bearer"]:
                return HTTPAuthorizationCredentials(
                    scheme=scheme, credentials=credentials
                )

        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="authorization 헤더에 Bearer 토큰 정보가 없습니다",
            )
        else:
            return None


def extract_token(request: Request) -> Token:
    token, token_type = (None, None)
    authorization: str = request.headers.get("Authorization")

    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme in ["Bearer"]:
            token = param
            token_type = scheme

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )

    return Token(token=token, type=token_type)


class AuthChallenge:
    def __call__(
        self,
        token: Token = Depends(extract_token),
    ):
        return self.get_current_user_id(token=token)


def get_current_user_id(token: Token) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="로그인 토큰이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return TokenData(user_id=user_id)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_expire_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt
