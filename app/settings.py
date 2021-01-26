from typing import Optional

from pydantic import AnyHttpUrl, BaseSettings, DirectoryPath, Field, stricturl


class Settings(BaseSettings):
    env: str = Field("prod", env="ENV")
    app_url: AnyHttpUrl = Field("http://127.0.0.1:8080", env="APP_URL")
    mongo_uri: Optional[
        stricturl(allowed_schemes={"mongodb"}, tld_required=False)
    ] = Field("mongodb://localhost:27018", env="MONGO_URI")
    catshtm_dir: Optional[DirectoryPath] = Field(None, env="CATSHTM_DIR")

    class Config:
        env_file = ".env"


settings = Settings()
