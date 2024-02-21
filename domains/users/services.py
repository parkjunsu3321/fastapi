from domains import Service
from fastapi import HTTPException, status

from .repositories import UserRepository
from .models import UserModel


class UserService(Service):
    def __init__(
        self,
        *,
        user_repository: UserRepository,
    ):
        self._user_repository = user_repository

    def get_user(self, *, user_id: int) -> UserModel:
        user = self._user_repository.get_user(user_id=user_id)

        # If the user is not found raise NotFound.
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Id not found",
            )

        return user

    def create_user(self, *, user_name, user_pw) -> int:
        user_id = self._user_repository.create_user(
            user_name=user_name,
            password=user_pw,
        )
        return user_id
