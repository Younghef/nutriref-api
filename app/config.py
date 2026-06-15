from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    usda_api_key: str
    usda_base_url: str = "https://api.nal.usda.gov/fdc/v1"

    # Default targets a host-local Redis (the common dev case). docker-compose
    # overrides this to redis://redis:6379/0 so the api container reaches the
    # `redis` service over the internal docker network.
    redis_url: str = "redis://localhost:6379/0"

    x402_network: str = "base-sepolia"
    x402_receiver_address: str
    x402_facilitator_url: str = "https://x402.org/facilitator"

    log_level: str = "INFO"


settings = Settings()
