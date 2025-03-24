from src.config.settings import Settings


class HostConfig(Settings):
    host: str = "localhost:8000"


host_config = HostConfig()
