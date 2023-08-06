from os import environ

from .context_var import is_production


class Env:
    def __init__(self) -> None:
        self._bot_token_dev = environ.get("DEV_BOT_TOKEN")
        self._bot_token_prod = environ.get("PROD_BOT_TOKEN")

    def get_bot_token(self) -> str | None:
        return self._bot_token_prod if is_production.get() else self._bot_token_dev
