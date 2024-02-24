from domains import Service
from fastapi import HTTPException, status

from .repositories import UserRepository
from .models import UserModel
from .repositories import GameResultRepository
from .models import GameResultModel

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
            user_pw=user_pw,
        )
        return user_id

class GameResultService(Service):
    def __init__(
        self,
        *,
        game_result_repository: GameResultRepository,
    ):
        self._game_result_repository = game_result_repository

    async def create_game_result(self, *, player_id: int, music_genre: str, score: int) -> int:
        order_data = await self._game_result_repository.create_game_result(
            player_id=player_id,
            music_genre=music_genre,
            score=score,
        )
        return order_data

    async def get_all_game_results(self) -> list[GameResultModel]:
        game_results = await self._game_result_repository.get_all_game_results()
        if not game_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No game results found",
                )
        return game_results
