import arrow
import random
from typing import List
from fastapi import APIRouter, HTTPException, status, Form, Depends, Query
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

class GenreForm(BaseModel):
    first_genre: str
    second_genre: str
    third_genre: str

class TextEmbed(BaseModel):
    input: str
    answer: str

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
async def getInfo(authorization: str = Header(...), db=Depends(provide_session)) -> UserItemGetResponse:
    user_service = UserService(user_repository=UserRepository(session=db))
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
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
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(f"/{name}/checklogin")
async def checklogin(authorization: str = Header(...), db=Depends(provide_session))->bool:
    user_service = UserService(user_repository=UserRepository(session=db))
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_check_login = user_service.get_user(user_id=user_id)
        if user_check_login is not None:
            return True
        return False
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

@router.delete(f"/{name}/delete_user")
async def delete_user(user_password: str = Query(...), authorization: str = Header(...), db=Depends(provide_session)):
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
async def Input_Genre(genre_data: GenreForm, authorization: str = Header(...),db=Depends(provide_session)):
    user_service = UserService(user_repository=UserRepository(session=db))
    try:
        genre_array = List[str]
        genre_array = [genre_data.first_genre, genre_data.second_genre, genre_data.third_genre]
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        Input_result = await user_service.Input_Genre(genres = genre_array, user_id=user_id)
        return Input_result
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.post(f"/{name}/create_list")
async def Create_List(request_data: dict, authorization: str = Header(...), db=Depends(provide_session)) -> List[List[str]]:
    game_music_service = GameMusicService(game_music_repository=GameMusicRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    level = request_data.get("level")
    chart_list: List[List[str]] = []  # chart_list 초기화
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        preferred_genre_list = await user_service.get_genre(user_id=user_id)
        game_list = await game_music_service.Level_design(level=level, preferred_genre_list=preferred_genre_list)
        if game_list is not None:  # game_list가 None이 아닐 때에만 반복문 실행
            for music in game_list:
                chart_list.append([music.game_music_id, music.game_music_link_fragment])  # chart_list에 요소 추가
        return chart_list
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def levenshtein_distance(s1, s2):
    """
    Compute the Levenshtein distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


@router.post(f"/{name}/textembedding")
async def textembedding(embedding: TextEmbed):
    try:
        levenshtein_dist = levenshtein_distance(embedding.input, embedding.answer)
        # 문자열 길이에 대한 유사성 계산
        max_len = max(len(embedding.input), len(embedding.answer))
        similarity_percentage = ((max_len - levenshtein_dist) / max_len) * 100
        return similarity_percentage >= 90 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(f"/{name}/input_result")
def input_result(request_data: int, authorization: str = Header(...), db=Depends(provide_session))->bool:
    score = request_data.get("score")
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        gameresult = GameResultService(user_repository=GameResultModel(session=db))
        result_data = gameresult.create_game_result(user_id=user_id, score=score)
        if result_data is not None:
            return True
        else:
            return False
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )