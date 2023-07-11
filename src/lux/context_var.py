from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from disnake import AppCmdInter

    from .bot import Lux
    from .env import Env
    from .mode import Modes

mode: "ContextVar[Modes]" = ContextVar("mode")
env: "ContextVar[Env]" = ContextVar("env")
bot: "ContextVar[Lux]" = ContextVar("bot")
interaction: "ContextVar[AppCmdInter]" = ContextVar("interaction")
