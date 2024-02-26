from typing import List
from domains import Service
from fastapi import HTTPException, status
from dependencies.auth import hash_password
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
        hashed_pw = hash_password(user_pw)
        user_id = self._user_repository.create_user(
            user_name=user_name,
            user_pw=hashed_pw,
        )
        return user_id
    
    async def change_password(self, *, user_id, new_pw) -> str:
        check_changing = await self._user_repository.change_password(user_id=user_id, new_password=new_pw)
        return check_changing
    
    async def delete_user(self, *, user_id):
        delete_user_result = await self._user_repository.delete_user(user_id=user_id)
        return delete_user_result

    def checkname_user(self, *, user_name) -> str:
        checking_name = self._user_repository.checkname_user(user_name=user_name)
        return checking_name

    def get_password(self, *, user_id) -> str:
        get_password = self._user_repository.get_password(user_id=user_id)
        return get_password

    async def Input_Genre(self, *, genres: List[str], user_id: int):
        Input_result = await self._user_repository.Input_Genre(genres = genres, user_id = user_id)
        return Input_result

    async def get_user_by_name(self, *, user_name: str) -> UserModel:
        user_entity = await self._user_repository.get_user_by_name(
            user_name=user_name,
        )
        return user_entity
    
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
