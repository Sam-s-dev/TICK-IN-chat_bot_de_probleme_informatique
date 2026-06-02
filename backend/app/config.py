from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "chatbot_user"
    DB_PASSWORD: str = "chatbot_password"
    DB_NAME: str = "chatbot_signalement"

    JWT_SECRET_KEY: str = "change_this_to_a_random_secret_key_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    ADMIN_EMAIL: str = "admin@centre-info.uganc.edu.gn"

    APP_NAME: str = "Chatbot Signalement UGANC"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
