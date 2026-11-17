from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", "../.env"], extra="ignore")

    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-me"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://ckpa:ckpa_pass@localhost:5432/ckpa_db"
    DATABASE_POOL_SIZE: int = 10

    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Model: gpt-4o (Option O1 - Selected CRM Context is strictly excluded from Base Scope per SRS §1.4 & §2.3)
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_MAX_INPUT_TOKENS: int = 6000
    LLM_MAX_OUTPUT_TOKENS: int = 900
    LLM_MAX_CALLS_PER_MONTH: int = 2000

    # --- RFP / SRS Runtime Bounds (Base Scope Only) ---
    APP_TIMEZONE: str = "Asia/Ho_Chi_Minh"
    ENABLE_ANSWER_STREAMING: bool = False

    LLM_MAX_CALLS_PER_PACKAGE: int = 2
    ANSWER_MAX_PASSAGES: int = 8
    ANSWER_MAX_PACKAGES_PER_MONTH: int = 1000
    PASSAGE_MAX_CHARS: int = 6000

    CORPUS_MAX_DOCUMENTS: int = 30
    CORPUS_MAX_PASSAGES: int = 300
    CORPUS_MAX_CRITICAL_FIELDS: int = 50

    IMPORT_OUTPUT_DIR: str = "data/output"
    IMPORT_MAX_ROWS_PER_BATCH: int = 500
    IMPORT_SNAPSHOT_STALENESS_HOURS: int = 25

    CACHE_WITHDRAWAL_MAX_SECONDS: int = 300
    PILOT_MAX_NAMED_USERS: int = 20
    PILOT_MAX_CONCURRENT_SESSIONS: int = 5
    SUPPORT_HOURS_START: str = "08:00"
    SUPPORT_HOURS_END: str = "17:00"

    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536

    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"


settings = Settings()
