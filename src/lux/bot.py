from pathlib import Path
from typing import TYPE_CHECKING, Any

from disnake.ext.commands import InteractionBot

from .context_var import bot, env
from .logger import default_logger

if TYPE_CHECKING:
    from logging import Logger
    from typing import Any, Self

    from .config import Config
    from .mode import Modes


class Lux(InteractionBot):
    def __init__(
        self,
        *,
        mode: "Modes",
        config: "Config",
        logger: "Logger" = default_logger,
        **options,
    ):
        is_dev = mode.is_dev()
        super().__init__(
            reload=is_dev, test_guilds=config.test_guilds if is_dev else None, **options
        )
        self.mode = mode
        self.config = config
        self.logger = logger

    def load_extension(self, name: str, *, package: str | None = None) -> None:
        self.logger.info(f"Loading extension {name}")
        super().load_extension(name, package=package)

    def load_extensions(self, path: str) -> None:
        if not (path_ := Path(path)).exists():
            raise ValueError(f"Provided path '{path_.resolve()}' does not exist")

        self.logger.info(f"Loading extensions from '{path_.resolve()}'")
        super().load_extensions(path)

    def reload_extension(self, name: str, *, package: str | None = None) -> None:
        self.logger.info(f"Reloading extension {name}")
        super().reload_extension(name, package=package)

    def unload_extension(self, name: str, *, package: str | None = None) -> None:
        self.logger.info(f"Unloading extension {name}")
        super().unload_extension(name, package=package)

    def init(self) -> "Self":
        self.load_extensions(self.config.extension_directory)
        bot.set(self)
        return self

    def run(self, *args: "Any", **kwargs: "Any") -> None:
        if not (token := env.get().get_bot_token(self.mode)):
            raise ValueError("No bot token provided")
        return super().run(token, *args, **kwargs)

    async def on_ready(self) -> None:
        self.logger.info("The bot is ready")
        self.logger.info(f"User: {self.user}")
        self.logger.info(f"User ID: {self.user.id}")
