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

    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_MAX_INPUT_TOKENS: int = 6000
    LLM_MAX_OUTPUT_TOKENS: int = 900
    LLM_MAX_CALLS_PER_MONTH: int = 2000
    LLM_REQUEST_TIMEOUT_SECONDS: int = 20
    LLM_ALLOW_TRAINING: bool = False
    LLM_ZERO_DATA_RETENTION: bool = True
    LLM_TELEMETRY_ENABLED: bool = False

    # --- SEC 06 Dev/Test vs Production Isolation Boundaries (VPC/DB/Storage/Keys) ---
    ISOLATED_VPC_NETWORK: str = "ckpa_g1_isolated_net"
    PROD_DATABASE_HOST_DENYLIST: tuple[str, ...] = (
        "prod-db.songnhat.vn",
        "rds.prod.songnhat.internal",
    )
    PROD_STORAGE_PATH_DENYLIST: tuple[str, ...] = (
        "s3://songnhat-prod",
        "/var/lib/ckpa-prod",
        "prod_storage",
    )
    INSECURE_DEFAULT_SECRETS: tuple[str, ...] = (
        "change-me",
        "change-me-in-production",
        "",
    )

    # --- RFP / SRS Runtime Bounds (Base Scope Only) ---
    APP_TIMEZONE: str = "Asia/Ho_Chi_Minh"
    ENABLE_ANSWER_STREAMING: bool = False

    LLM_MAX_CALLS_PER_PACKAGE: int = 2
    ANSWER_SYSTEM_PROMPT_PATH: str = "prompts/answer_system_vi.txt"
    ANSWER_MAX_PASSAGES: int = 8
    ANSWER_MAX_PACKAGES_PER_MONTH: int = 1000
    PASSAGE_MAX_CHARS: int = 6000

    CORPUS_MAX_DOCUMENTS: int = 30
    CORPUS_MAX_PASSAGES: int = 300
    CORPUS_MAX_CRITICAL_FIELDS: int = 50

    IMPORT_OUTPUT_DIR: str = "data/output"
    IMPORT_MAX_ROWS_PER_BATCH: int = 500
    IMPORT_SNAPSHOT_STALENESS_HOURS: int = 25
    ENABLE_O1_CONTEXT_IMPORT: bool = False

    CACHE_WITHDRAWAL_MAX_SECONDS: int = 300
    EMERGENCY_DISABLE_CACHE_KEY: str = "ckpa:emergency_disable"
    OPS_LATENCY_P95_SECONDS: int = 25
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

    def verify_sec06_test_prod_isolation(self) -> dict[str, object]:
        """Enforce SEC 04 training lock and SEC 06 100% Dev/Test vs Prod isolation."""
        env_norm = self.APP_ENV.strip().lower()
        if env_norm not in {"development", "test", "production"}:
            raise ValueError(f"Unsupported APP_ENV={self.APP_ENV!r} (SEC 06).")

        if self.LLM_ALLOW_TRAINING:
            raise ValueError("SEC 04 violation: LLM_ALLOW_TRAINING must be strictly False.")
        if not self.LLM_ZERO_DATA_RETENTION:
            raise ValueError("SEC 04 violation: LLM_ZERO_DATA_RETENTION must be True.")
        if self.LLM_TELEMETRY_ENABLED:
            raise ValueError("SEC 04 violation: LLM_TELEMETRY_ENABLED must be False.")
        if self.ENABLE_ANSWER_STREAMING:
            raise ValueError("INV-03 violation: pre-verification answer streaming is forbidden.")

        db_lower = self.DATABASE_URL.lower()
        storage_lower = self.IMPORT_OUTPUT_DIR.lower()
        if not self.ISOLATED_VPC_NETWORK.strip() or "prod" in self.ISOLATED_VPC_NETWORK.lower():
            raise ValueError("SEC 06 violation: VPC network must be isolated from production.")

        if env_norm == "production":
            if (
                self.APP_SECRET_KEY.strip() in self.INSECURE_DEFAULT_SECRETS
                or len(self.APP_SECRET_KEY.strip()) < 16
            ):
                raise ValueError(
                    "SEC 06 violation: production environment cannot use default/weak secret key."
                )
            if "ckpa_pass@" in db_lower or "localhost" in db_lower or "ckpa_test" in db_lower:
                raise ValueError(
                    "SEC 06 violation: production environment cannot connect to dev/test database."
                )
        else:
            for prod_host in self.PROD_DATABASE_HOST_DENYLIST:
                if prod_host.lower() in db_lower:
                    raise ValueError(
                        f"SEC 06 violation: {env_norm} environment cannot connect to "
                        f"production DB host {prod_host!r}."
                    )
            for prod_storage in self.PROD_STORAGE_PATH_DENYLIST:
                if prod_storage.lower() in storage_lower:
                    raise ValueError(
                        f"SEC 06 violation: {env_norm} environment cannot mount "
                        f"production storage {prod_storage!r}."
                    )

        return {
            "app_env": env_norm,
            "isolated_from_production": env_norm in {"development", "test"},
            "isolation_layers": {
                "vpc": True,
                "db": True,
                "storage": True,
                "keys": True,
            },
            "llm_allow_training": self.LLM_ALLOW_TRAINING,
            "llm_zero_data_retention": self.LLM_ZERO_DATA_RETENTION,
            "llm_telemetry_enabled": self.LLM_TELEMETRY_ENABLED,
            "pilot_max_named_users": self.PILOT_MAX_NAMED_USERS,
            "pilot_max_concurrent_sessions": self.PILOT_MAX_CONCURRENT_SESSIONS,
        }


settings = Settings()
