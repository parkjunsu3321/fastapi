import arrow
from fastapi import APIRouter, HTTPException, status, Form, Depends
from dependencies.database import provide_session
from fastapi import Header
from jose import JWTError, jwt
from domains.users.services import UserService
from domains.users.repositories import UserRepository
from domains.users.dto import (
    UserItemGetResponse,
    UserPostRequest,
    UserPostResponse,
)
from dependencies.database import provide_session
from dependencies.config import get_config
from dependencies.auth import(
    Token,
    verify_password,
    create_access_token,
    ALGORITHM,
)
from domains.users.dto import GameResultItemGetResponse
from domains.users.services import GameResultService
from domains.users.repositories import GameResultRepository
from pydantic import BaseModel

class LoginForm(BaseModel):
    user_name: str
    user_password: str

conf_vars = get_config()
secret_key = conf_vars.jwt_secret_key
name = "users"
result = "result"
router = APIRouter()

@router.post(f"/{name}/create")
async def create(
    payload: UserPostRequest,
    db=Depends(provide_session),
) -> UserPostResponse:
    user_service = UserService(user_repository=UserRepository(session=db))

    user_id = await user_service.create_user(
        user_name=payload.user_name,
        user_pw=payload.user_password,
    )

    return UserPostResponse(id=user_id).dict()


@router.get(f'/{result}/{"all"}')
async def get(db=Depends(provide_session)):
    gameresult_service = GameResultService(game_result_repository=GameResultRepository(session=db))
    game_result_info = await gameresult_service.get_all_game_results()
    
    if game_result_info:
        return GameResultItemGetResponse(
            data=GameResultItemGetResponse.DTO(
                order_data=game_result_info.order_data,
                game_result_player_id=game_result_info.game_result_player_id,
                game_result_music_id=game_result_info.game_result_music_id,
                game_result_score=game_result_info.game_result_score,
                game_result_created_time=str(game_result_info.game_result_created_time),  # Convert to string
            )
        ).dict()
    else:
        return {"message": "게임 결과를 찾을 수 없습니다."}  # Or any appropriate response

@router.get("/test/") 
async def apiTest():
    return "testing"

@router.get("/") 
async def apiTest():
    return {"hello":"world"}


@router.get(f"/{name}/getInfo") 
async def plz(db=Depends(provide_session)):
    user_service = UserService(user_repository=UserRepository(session=db))
    user_info = await user_service.get_user(user_id=3321)
    
    if user_info:
        return UserItemGetResponse(
            data=UserItemGetResponse.DTO(
                id=user_info.id,
                name=user_info.name,
                flavor_genre_first=user_info.flavor_genre_first or "",  # If None, set to empty string
                flavor_genre_second=user_info.flavor_genre_second or "",  # If None, set to empty string
                flavor_genre_third=user_info.flavor_genre_third or "",  # If None, set to empty string
                created_at=str(user_info.created_at),  # Convert to string
                updated_at=str(user_info.updated_at),  # Convert to string
            )
        ).dict()
    else:
        return {"message": "User not found"}  # Or any appropriate response
    

@router.post(f"/{name}/protected_endpoint")
async def protected_endpoint(authorization: str = Header(...)):
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode_jwt(token, secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        # 여기서 user_id를 사용하여 해당 사용자의 데이터를 처리하거나 작업을 수행할 수 있습니다.
        return {"message": f"Welcome user {user_id} to the protected endpoint"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.post(f"/{name}/login")
async def login(
    login_data: LoginForm,
    db=Depends(provide_session),
) -> Token:
    user_service = UserService(user_repository=UserRepository(session=db))
    user = user_service.get_user_by_name(user_name=login_data.user_name)

    if not verify_password(login_data.user_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 틀립니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})
    return Token(token=access_token, type="bearer")
#보안..이슈..