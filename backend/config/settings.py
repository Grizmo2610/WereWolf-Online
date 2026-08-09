import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    env: str = os.getenv("ENV", "development")

    d1_account_id: str = os.getenv("D1_ACCOUNT_ID", "")
    d1_database_id: str = os.getenv("D1_DATABASE_ID", "")
    d1_api_token: str = os.getenv("D1_API_TOKEN", "")

    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_expire_days: int = int(os.getenv("JWT_EXPIRE_DAYS", "7"))

    snapshot_encryption_key: str = os.getenv("SNAPSHOT_ENCRYPTION_KEY", "")

    local_sqlite_path: str = os.path.join(os.path.dirname(__file__), "..", "db", "local_dev.sqlite3")

    @property
    def use_d1(self) -> bool:
        return bool(self.d1_account_id and self.d1_database_id and self.d1_api_token)


settings = Settings()
