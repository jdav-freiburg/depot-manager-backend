from datetime import time
from typing import Optional, List, Any, Literal

from pydantic import BaseModel, Field

type Loglevel = Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

TORTOISE_ORM = {
    "connections": {"default": "sqlite://devdepot.sqlite"},
    "apps": {
        "depot": {
            "models": ["depot_server.db2.models"],
            "default_connection": "default",
            "migrations": "depot_server.db2.migrations",
        }
    },
}

class MongoConfig(BaseModel):
    uri: str = Field(...)

class MailConfig(BaseModel):
    host: str = Field(...)
    port: Optional[int] = None
    sender: str = Field(...)

    ssl: bool = False
    starttls: bool = False
    keyfile: Optional[str] = None
    certfile: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

class OAuth2ClientConfig(BaseModel):
    client_id: str
    client_secret: Optional[str] = None
    request_token_url: Optional[str] = None
    request_token_params: Optional[str] = None
    access_token_url: Optional[str] = None
    access_token_params: Optional[str] = None
    refresh_token_url: Optional[str] = None
    refresh_token_params: Optional[str] = None
    authorize_url: Optional[str] = None
    authorize_params: Optional[str] = None
    api_base_url: Optional[str] = None
    server_metadata_url: Optional[str] = None

    teams_property: str = 'teams'


class DbConfig(BaseModel):
    engine: str = Field(...)
    host: Optional[str] = None
    port: Optional[int] = Field(default=5432)
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = Field(description="Name of the database or path to sqlite file")

    def to_tortoise_config(self) -> dict[str, Any]:
        if self.engine == 'postgresql':
            return {
                'connections': {
                    'default': f'postgres://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}',
                },
                'apps': {
                    'models': {
                        'models': ['depot_server.db2.models'],
                        'default_connection': 'default',
                    },
                },
            }
        elif self.engine == 'sqlite':
            return {
                'connections': {
                    'default': f'sqlite://{self.database}',
                },
                'apps': {
                    'models': {
                        'models': ['depot_server.db2.models', ],
                        'default_connection': 'default',
                    },
                },
            }
        else:
            raise ValueError(f"Unsupported database engine: {self.engine}")


class CosmeticsConfig(BaseModel):
    tag_default_color: str = Field(default="#1683E9",
                                   description="Default color for tags in hex format, e.g. #FF0000",
                                   max_length=7)

class Config(BaseModel):
    debug: bool = Field(default=False,
                        description="Enable debug mode. Enables adhoc creation of db models instead of using migrations")
    mongo: MongoConfig = Field(...)
    mail: MailConfig = Field(...)
    oauth2: OAuth2ClientConfig = Field(...)
    db: DbConfig = Field(...)
    cosmetics: CosmeticsConfig = Field(...)
    frontend_base_url: str = Field(...)
    allow_origins: List[str] = Field(...)
    log_level: Loglevel = Field(default="INFO")

    return_reservation_reminder_cron_time: time = Field(...)

    reservation_code_length: int = Field(...)
    reservation_code_chars: str = Field(...)
    reservation_automatic_return: bool = Field(...)

    device_api_key: Optional[str] = Field(...)
