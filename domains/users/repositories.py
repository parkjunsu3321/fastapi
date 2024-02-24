from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.future import select
from .models import UserModel
from .models import GameResultModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, *, user_id: int):
        async with self._session.begin():
            result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
            user = result.scalars().first()
            return user

    async def create_user(self, *, user_name: str, user_pw: str):
        async with self._session.begin():
            user_entity = UserModel(name=user_name, password=user_pw)
            self._session.add(user_entity)
            await self._session.commit()
            return user_entity.id
        
    async def checkname_user(self, *, user_name: str):
        async with self._session.begin():
            # 기존에 해당 이름의 사용자가 있는지 확인
            query = await self._session.execute(select(UserModel).filter_by(name=user_name))
            existing_user = await query.fetchone()
    
            if existing_user is not None:
                # 이미 사용자가 존재하므로 중복되었다고 판단하여 False 반환
                return False
    
            # 사용자가 존재하지 않으므로 True 반환
            return True

    
    async def get_user_by_name(self, *, user_name: str):
        async with self._session.begin():
            query = select(UserModel).filter(UserModel.name == user_name)
            result = await self._session.execute(query)
            user = result.scalars().first()
        
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="유저 정보가 없습니다.",
                )
            return user

class GameMusicRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    

class GameResultRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_game_result(self, *, player_id: int, music_genre: str, score: int):
        async with self._session.begin():
            last_order_data = await self._session.execute(select(func.max(GameResultModel.order_data)).scalar())

            if last_order_data is None:
                order_data = 0
            else:
                order_data = last_order_data + 1

            game_result_entity = GameResultModel(
                order_data=order_data,
                game_result_player_id=player_id,
                game_result_music_id=music_genre,
                game_result_socre=score
            )

            self._session.add(game_result_entity)
            await self._session.commit()

            return order_data

    async def get_all_game_results(self) -> list[GameResultModel]:
        async with self._session.begin():
            query = select(GameResultModel)
            return (await self._session.execute(query)).scalars().all()


