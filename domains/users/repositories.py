from sqlalchemy.ext.asyncio import AsyncSession
from .models import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, *, user_id: int):
        async with self._session() as session:
            result = await session.execute(
                select(UserModel).filter(UserModel.id == user_id)
            )
            return result.scalar_one_or_none()

    async def create_user(self, *, user_name: str, password: str):
        async with self._session() as session:
            user_entity = UserModel(
                name=user_name,
                password=password,
            )
            session.add(user_entity)
            await session.commit()
            return user_entity.id
