import arrow
from typing import List
from fastapi import APIRouter, HTTPException, status, Form, Depends
from dependencies.database import provide_session
from fastapi import Header
from jose import JWTError
import jwt
from domains.users.services import UserService
from domains.users.repositories import UserRepository
from domains.users.dto import (
    UserItemGetResponse,
    UserPostRequest,
    UserPostResponse,
    UserPostGenre,
)
from dependencies.database import provide_session
from dependencies.config import get_config
from dependencies.auth import(
    Token,
    verify_password,
    create_access_token,
    hash_password,
    ALGORITHM,
)
from domains.users.dto import GameResultItemGetResponse
from domains.users.services import GameResultService
from domains.users.repositories import GameResultRepository
from domains.users.services import GameResultService
from domains.users.repositories import GameMusicRepository
from domains.users.services import GameMusicService
from pydantic import BaseModel
from domains.users.models import GameResultModel
from domains.users.models import GameMusicModel

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

@router.post(f"/{name}/checkId")
async def checkId(
    payload: UserPostRequest,
    db=Depends(provide_session),
) -> bool:
    user_service = UserService(user_repository=UserRepository(session=db))

    checking = await user_service.checkname_user(
        user_name=payload.user_name,
    )
    return checking

@router.get(f'/{result}/all')
async def get(db=Depends(provide_session)):
    gameresult_service = GameResultService(game_result_repository=GameResultRepository(session=db))
    game_result_info = await gameresult_service.get_all_game_results()
    sortting_game_result = await SettingGameResult(game_results=game_result_info)
    if sortting_game_result is not None:
        return sortting_game_result
    else:
        return None

async def SettingGameResult(game_results: List[GameResultModel]) -> List[GameResultModel]:
    sorted_results = sorted(game_results, key=lambda x: x.game_result_score, reverse=True)
    top_seven_results = sorted_results[:7]
    return top_seven_results


@router.get("/test/") 
async def apiTest():
    return "testing"

@router.get("/") 
async def apiTest():
    return {"hello":"world"}


@router.post(f"/{name}/getInfo")
async def getInfo(user_id, db=Depends(provide_session),) -> UserItemGetResponse:
    user_service = UserService(user_repository=UserRepository(session=db))
    user_info = await user_service.get_user(user_id=user_id)
    
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
    print(authorization)
    try:
        token = authorization.split("Bearer ")[1]
        print(token)
        print(secret_key,ALGORITHM)
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        print("a")
        user_id: int = payload.get("sub")
        print(payload.get("sub"))
        # 여기서 user_id를 사용하여 해당 사용자의 데이터를 처리하거나 작업을 수행할 수 있습니다.
        return {"message": f"Welcome user {user_id} to the protected endpoint"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.post(f"/{name}/check_passwrod")
async def check_passwrod(request_data: dict, authorization: str = Header(...), db=Depends(provide_session)):
    user_password = request_data.get("user_password")
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_service = UserService(user_repository=UserRepository(session=db))
        get_password = await user_service.get_password(user_id=user_id)
        if not verify_password(user_password, get_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비밀번호가 틀립니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(f"/{name}/changing_password")
async def check_passwrod(request_data: dict, authorization: str = Header(...), db=Depends(provide_session))->bool:
    new_password = request_data.get("new_password")
    try:
        hasded_new_pw = hash_password(new_password)
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_service = UserService(user_repository=UserRepository(session=db))
        chaning_pw = await user_service.change_password(user_id=user_id, new_pw=hasded_new_pw)
        if chaning_pw == hasded_new_pw:
            print(chaning_pw)
            print(hasded_new_pw)
            return True
        else:
            return False
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(f"/{name}/delete_user")
async def delete_user(request_data: dict, authorization: str = Header(...), db=Depends(provide_session)):
    user_password = request_data.get("user_password")
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_service = UserService(user_repository=UserRepository(session=db))
        get_password = await user_service.get_password(user_id=user_id)
        if not verify_password(user_password, get_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비밀번호가 틀립니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        delete_user_data = await user_service.delete_user(user_id=user_id)
        return delete_user_data
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
    user = await user_service.get_user_by_name(user_name=login_data.user_name)
    
    if not verify_password(login_data.user_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 틀립니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})
    return Token(token=access_token, type="bearer")

@router.post(f"/{name}/Input_Genre")
async def Input_Genre(genre_array: UserPostGenre, authorization: str = Header(...),db=Depends(provide_session)):
    user_service = UserService(user_repository=UserRepository(session=db))
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        print("a")
        user_id: int = payload.get("sub")
        Input_result = await user_service.Input_Genre(genres = genre_array.genres, user_id=user_id)
        return Input_result
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.post(f"/{name}/create_list")
async def Create_List(request_data: dict, authorization: str = Header(...), db=Depends(provide_session)) -> List[str]:
    game_music_service = GameMusicService(game_music_repository=GameMusicRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    level = request_data.get("level")
    chart_list: List[str] = []  # chart_list 초기화
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_genre_list = await user_service.get_genre(user_id=user_id)
        game_list = await game_music_service.Level_design(level=level, preferred_genre_list=user_genre_list)
        if game_list is not None:  # game_list가 None이 아닐 때에만 반복문 실행
            for music in game_list:
                chart_list.append(music.game_music_id)  # chart_list에 요소 추가
        return chart_list
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
