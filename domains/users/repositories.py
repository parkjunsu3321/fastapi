from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import UserModel

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

class GameMusicRepository:
    def __init__(self, session: Session):
        self._session = session

class GameResultRepository:
    def __init__(self, session: Session):
        self._session = session

    def create_game_result(self, *, player_id: int, music_genre: str, score: int):
        # 테이블에서 마지막 게임 결과의 순서를 조회합니다.
        last_order_data = self._session.query(func.max(GameResultModel.order_data)).scalar()
        
        # 테이블이 비어있는 경우 order_data를 0으로 초기화합니다.
        if last_order_data is None:
            order_data = 0
        else:
            # 마지막 게임 결과의 순서에 +1을 해서 새로운 order_data를 생성합니다.
            order_data = last_order_data + 1

        game_result_entity = GameResultModel(
            order_data=order_data,
            game_result_player_id=player_id,
            game_result_music_id=music_genre,
            game_result_socre=score
        )

        self._session.add(game_result_entity)
        self._session.commit()

        return order_data

    def get_game_results_for_player(self, *, player_id: int):
        return (
            self._session.query(GameResultModel)
            .filter(GameResultModel.game_result_player_id == player_id)
            .all()
        )
    

    
    
