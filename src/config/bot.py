from src.config.settings import Settings


class BotConfig(Settings):
    bot_token: str = ""


bot_config = BotConfig()
