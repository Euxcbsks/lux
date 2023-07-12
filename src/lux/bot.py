from pathlib import Path
from typing import TYPE_CHECKING, Any

from disnake.ext.commands import InteractionBot
from disnake.ext.commands.errors import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError,
)

from .context_var import bot, env, interaction
from .logger import default_logger

if TYPE_CHECKING:
    from logging import Logger
    from typing import Any, Callable, Self

    from disnake import AppCmdInter

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
        self._unloaded_extensions = list[str]()

    @property
    def unloaded_extensions(self) -> list[str]:
        return self._unloaded_extensions

    def _try_extension(
        self, operation: "Callable", name: str, *, package: str | None = None
    ):
        logger = self.logger

        try:
            operation(name, package=package)
        except ExtensionNotFound:
            logger.error(f"Extension '{name}' not found")
        except ExtensionNotLoaded:
            logger.error(f"Extension '{name}' not loaded")
        except ExtensionAlreadyLoaded:
            logger.error(f"Extension '{name}' already loaded")
        except NoEntryPointError:
            logger.error(f"Extension '{name}' has no entry point ('setup' function)")
        except ExtensionFailed as e:
            logger.exception(f"Extension '{name}' failed to load", e)

    def load_extension(self, name: str, *, package: str | None = None) -> None:
        self.logger.info(f"Loading extension '{name}'")
        self._try_extension(super().load_extension, name, package=package)

    def load_extensions(self, path: str) -> None:
        if not (path_ := Path(path).resolve()).exists():
            raise ValueError(f"Provided path '{path_}' does not exist")

        self.logger.info(f"Loading extensions from '{path_}'")
        super().load_extensions(path)

    def reload_extension(self, name: str, *, package: str | None = None) -> None:
        self.logger.info(f"Reloading extension '{name}'")
        self._try_extension(super().reload_extension, name, package=package)

    def unload_extension(self, name: str, *, package: str | None = None) -> None:
        self.logger.info(f"Unloading extension '{name}'")
        self._unloaded_extensions.append(name)
        self._try_extension(super().unload_extension, name, package=package)

    def init(self) -> "Self":
        bot.set(self)
        self.load_extensions(self.config.extension_directory)
        return self

    def run(self, *args: "Any", **kwargs: "Any") -> None:
        if not (token := env.get().get_bot_token(self.mode)):
            raise ValueError("No bot token provided")
        return super().run(token, *args, **kwargs)

    async def on_ready(self) -> None:
        self.logger.info("The bot is ready")
        self.logger.info(f"User: {self.user}")
        self.logger.info(f"User ID: {self.user.id}")

    async def on_application_command(self, inter: "AppCmdInter"):
        interaction.set(inter)
        await self.process_application_commands(inter)
