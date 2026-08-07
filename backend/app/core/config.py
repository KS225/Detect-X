from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "DetectX AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Web Application Security Assessment Platform"

    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = AppConfig()