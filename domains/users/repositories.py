from sqlalchemy.ext.asyncio import AsyncSession
from .models import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, *, user_id: int):
        async with self._session() as session:  # Create session properly
            return (
                await session.query(UserModel)
                .filter(UserModel.id == user_id)
                .first()
            )

    async def create_user(self, *, user_name: str, user_pw: str):
        async with self._session() as session:  # Create session properly
            user_entity = UserModel(name=user_name, password=user_pw)
            session.add(user_entity)
            await session.commit()
            return user_entity.id
