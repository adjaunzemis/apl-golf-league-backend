from pydantic import BaseSettings

class Settings(BaseSettings):
    apl_golf_league_api_url: str
    apl_golf_league_api_database_connector: str
    apl_golf_league_api_database_user: str
    apl_golf_league_api_database_password: str
    apl_golf_league_api_database_url: str
    apl_golf_league_api_database_port_external: int
    apl_golf_league_api_database_port_internal: int
    apl_golf_league_api_database_name: str
    apl_golf_league_api_database_echo: bool = True
    apl_golf_league_api_access_token_secret_key: str
    apl_golf_league_api_access_token_algorithm: str
    apl_golf_league_api_access_token_expire_minutes: int = 120
    mail_username: str
    mail_password: str
    mail_from_address: str
    mail_from_name: str
    mail_server: str
    mail_port: int

    class Config:
        env_file = ".env"
