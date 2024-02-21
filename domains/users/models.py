from sqlalchemy import Column, DateTime, String, Integer, func


from dependencies.database import Base


class UserModel(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    flavor_genre_first = Column(String)
    flavor_genre_second = Column(String)
    flavor_genre_third = Column(String)
    created_at = Column(DateTime, server_default=func.utc_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.utc_timestamp(),
        server_onupdate=func.utc_timestamp(),
    )

class Game_Music_TableModel(Base):
    __tablename__ = "game_music"

    game_music_id = Column(String, primary_key=True, nullable=False)
    game_music_link_fragment = Column(String, nullable=False)
    game_music_genre_name = Column(String, nullable=False)
    game_music_created_at = Column(DateTime, server_default=func.utc_timestamp())
    game_music_updated_at = Column(
        DateTime,
        server_default=func.utc_timestamp(),
        server_onupdate=func.utc_timestamp(),
    )

