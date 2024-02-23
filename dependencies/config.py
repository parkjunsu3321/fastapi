import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class DefaultConfig(BaseSettings):
    postgresql_endpoint: str = os.getenv("POSTGRESQL_ENDPOIN", "svc.sel4.cloudtype.app")
    postgresql_port: int = os.getenv("POSTGRESQL_POR", 32752)
    postgresql_table: str = os.getenv("POSTGRESQL_TABL", "reaction_db")
    postgresql_user: str = os.getenv("POSTGRESQL_USE", "root")
    postgresql_password: int = os.getenv("POSTGRESQL_PASSWOR", 3321)

@lru_cache
def get_config():
    return DefaultConfig()
