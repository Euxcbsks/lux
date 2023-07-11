from os import environ
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mode import Modes


class Env:
    def __init__(self) -> None:
        self._bot_token_dev = environ.get("DEV_BOT_TOKEN")
        self._bot_token_prod = environ.get("PROD_BOT_TOKEN")

    def get_bot_token(self, mode: "Modes") -> str | None:
        return self._bot_token_dev if mode.is_dev() else self._bot_token_prod
