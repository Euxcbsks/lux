from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from disnake import AppCmdInter

    from .bot import Lux
    from .env import Env

is_production: "ContextVar[bool]" = ContextVar("is_production")
env: "ContextVar[Env]" = ContextVar("env")
bot: "ContextVar[Lux]" = ContextVar("bot")
interaction: "ContextVar[AppCmdInter]" = ContextVar("interaction")
