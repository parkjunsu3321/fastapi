from sqlalchemy.orm import Session
from .models import UserModel


class UserRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_user(self, *, user_id: int):
        return (
            self._session.query(UserModel)
            .filter(
                UserModel.id == user_id,
            )
            .first()
        )

    def create_user(self, *, user_name: str, password: str):
        user_entity = UserModel(
            name=user_name,
            password=password,
        )

        self._session.add(user_entity)
        self._session.commit()

        return user_entity.id
