from fastapi import APIRouter, Depends
from dependencies.database import provide_session

from domains.users.services import UserService
from domains.users.repositories import UserRepository
from domains.users.dto import (
    UserItemGetResponse,
    UserPostRequest,
    UserPostResponse,
)

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


@router.get(f"/{name}/{{user_id}}")
async def get(
    user_id,
    db=Depends(provide_session),
) -> UserItemGetResponse:
    user_service = UserService(user_repository=UserRepository(session=db))

    user_info = user_service.get_user(user_id=user_id)

    return UserItemGetResponse(
        data=UserItemGetResponse.DTO(
            id=user_info.id,
            name=user_info.name,
            flavor_genre_first=user_info.flavor_genre_first,
            flavor_genre_second=user_info.flavor_genre_second,
            flavor_genre_third=user_info.flavor_genre_third,
            created_at=user_info.created_at,
            updated_at=user_info.updated_at,
        )
    ).dict()
