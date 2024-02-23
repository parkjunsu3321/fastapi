from sqlalchemy import Column, DateTime, String, Integer, func


from dependencies.database import Base


class UserModel(Base):
    __tablename__ = "users"

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

class GameMusicModel(Base):
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

class GameResultModel(Base):
    __tablename__ = "game_result"

    order_data = Column(Integer, primary_key=True, nullable=False)
    game_result_player_id = Column(String, nullable=False)
    game_result_music_id = Column(String, nullable=False)
    game_result_score = Column(Integer, nullable=False)
    game_result_created_time = Column(DateTime, server_default=func.utc_timestamp())
