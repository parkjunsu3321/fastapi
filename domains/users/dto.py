from pydantic import BaseModel


class UserItemGetResponse(BaseModel):
    class DTO(BaseModel):
        id: int
        name: str
        flavor_genre_first: str
        flavor_genre_second: str
        flavor_genre_third: str
        created_at: str
        updated_at: str

    data: DTO


class UserPostRequest(BaseModel):
    user_name: str
    user_password: str


class UserPostResponse(BaseModel):
    id: int



class GameMusicItemGetResponse(BaseModel):
    class DTO(BaseModel):
        game_music_id: str
        game_music_link_fragment: str
        game_music_genre_name: str
        game_music_created_at: str
        game_music_updated_at: str
    data: DTO


class GameResultItemGetResponse(BaseModel):
    class DTO(BaseModel):
        order_data: int
        game_result_player_id: str
        game_result_music_id: str
        game_result_score: int
        game_result_created_time: str

    data: DTO