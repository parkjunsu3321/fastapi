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
