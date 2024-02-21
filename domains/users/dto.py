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
