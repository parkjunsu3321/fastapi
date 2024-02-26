from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.future import select
from .models import UserModel
from .models import GameResultModel
from .models import GameMusicModel
from sqlalchemy import func

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, *, user_id: int):
        user_id = int(user_id)
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
            existing_user = query.fetchone()  # 수정된 부분
    
            if existing_user is not None:
                # 이미 사용자가 존재하므로 중복되었다고 판단하여 False 반환
                return False
    
            # 사용자가 존재하지 않으므로 True 반환
            return True

    async def get_password(self, *, user_id: int) -> str:
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user_password = query.scalar().password

            if user_password is not None:
                return user_password 
        return None

    async def change_password(self, *, user_id: int, new_password: str):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                user.password = new_password
                return user.password
        return None

    async def delete_user(self, *, user_id: int):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                await self._session.delete(user)
                await self._session.flush()  # 변경 사항을 일시적으로 세션에 반영
                await self._session.commit()  # 유저 삭제 후에 세션을 커밋
                return True  # 삭제 작업이 성공적으로 수행됨을 반환
        return False  # 삭제 작업 실패

    async def Input_Genre(self, *, genres: List[str], user_id: str):
        async with self._session.begin():
            query = select(UserModel).filter(UserModel.id == user_id)
            result = await self._session.execute(query)
            user = result.scalar()
            if user is not None:
                user.flavor_genre_first = genres[0]
                user.flavor_genre_second = genres[1]
                user.flavor_genre_third = genres[2]
                return True
            else:
                return False

    async def get_genre(self, *, user_id: int)->List[str]:
        returnValue = List[str]
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await self._session.execute(query)
        user = result.scalar()
        returnValue = [user.flavor_genre_first, user.flavor_genre_second, user.flavor_genre_third]
        return returnValue

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
    
    async def NormalGameListObj(self) -> List[GameMusicModel]:
        game_music_list = []
        genres = ["발라드", "힙합", "댄스", "락", "R&B"]
        for genre in genres:
            # 각 장르에서 랜덤하게 2개의 음악을 선택
            query = (
                select(GameMusicModel)
                .filter(GameMusicModel.game_music_genre_name == genre)
                .order_by(func.random())
                .limit(2)
            )
            result = await self._session.execute(query)
            selected_music = result.scalars().all()
            if selected_music:
                game_music_list.extend(selected_music)
        return game_music_list

    async def EasyGameListObj(self, *, preferred_genre_list: List[str]) -> List[GameMusicModel]:
        game_music_list = []
        for i, genre in enumerate(preferred_genre_list):
            query = (
                select(GameMusicModel)
                .filter(GameMusicModel.game_music_genre_name == genre)
                .order_by(func.random())
            )
                            # 선호하는 장르의 수에 따라 선택할 game_music_id의 개수 설정
            if i == 0:
                limit = 4
            elif i == 1:
                limit = 3
            elif i == 2:
                limit = 2
            else:
                limit = 1
            result = await self._session.execute(query.limit(limit))
            selected_music = result.scalars().all()
            if selected_music:
                game_music_list.extend(selected_music)
        return game_music_list
        
    async def HardGameListObj(self, *, preferred_genre_list: List[str]) -> List[GameMusicModel]:
        game_music_list = []
        excluded_genres = [genre for genre in ["발라드", "힙합", "댄스", "락", "R&B"] if genre not in preferred_genre_list]
        for genre in excluded_genres:
            query = (
                select(GameMusicModel)
                .filter(GameMusicModel.game_music_genre_name == genre)
                .order_by(func.random())
                .limit(10)
            )
            result = await self._session.execute(query)
            selected_music = result.scalars().all()
            if selected_music:
                game_music_list.extend(selected_music)
        return game_music_list


    async def Level_design(self, *, level: int, preferred_genre_list: List[str]):
        async with self._session.begin():
            if level == 1:
                game_list = await self.EasyGameListObj(preferred_genre_list=preferred_genre_list)
            elif level == 2:
                game_list = await self.NormalGameListObj()
            elif level == 3:
                return True
            return game_list
            

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


