from fastapi import APIRouter, Depends
from dependencies.database import provide_session

from domains.users.services import UserService
from domains.users.repositories import UserRepository
from domains.users.dto import (
    UserItemGetResponse,
    UserPostRequest,
    UserPostResponse,
)

from domains.users.dto import GameResultItemGetResponse
from domains.users.services import GameResultService
from domains.users.repositories import GameResultRepository


name = "users"
router = APIRouter()

@router.post(f"/{name}/create")
async def create(
    payload: UserPostRequest,
    db=Depends(provide_session),
) -> UserPostResponse:
    user_service = UserService(user_repository=UserRepository(session=db))

    user_id = user_service.create_user(
        user_name=payload.user_name,
        user_pw=payload.user_password,
    )

    return UserPostResponse(id=user_id).dict()


@router.get(f'/{name}/{"all"}')
async def get(order_data: int, db=Depends(provide_session)):
    gameresult_service = GameResultService(game_result_repository=GameResultRepository(session=db))
    game_result_info = await gameresult_service.get_game_result(order_data=order_data)
    
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



@router.get("/apiawake")  # Renamed the endpoint for clarity
async def apiawake(db=Depends(provide_session)):
    user_service = GameResultService(user_repository=UserRepository(session=db))
    user_info = await user_service.get_user(user_id=3321)
    
    if user_info:
        return GameResultItemGetResponse(
            data=GameResultItemGetResponse.DTO(
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

@router.get("/test/") 
async def apiTest():
    return "testing"

@router.get("/") 
async def apiTest():
    return {"hello":"world"}


@router.get("/plz") 
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