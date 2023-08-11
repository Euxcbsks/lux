from pathlib import Path
from typing import TYPE_CHECKING

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
from .utility import Development

if TYPE_CHECKING:
    from logging import Logger
    from typing import Any, Callable, Self

    from disnake import AppCmdInter

    from .config import CogConfig, Config


class Lux(InteractionBot):
    def __init__(
        self,
        *,
        production: bool,
        config: "Config",
        cog_config: "CogConfig",
        logger: "Logger" = default_logger,
        disable_debug_extra_init: bool = False,
        **options,
    ):
        super().__init__(
            reload=not production,
            test_guilds=None if production else config.test_guilds,
            intents=config.intents,
            **options,
        )
        self._production = production
        self._config = config
        self._cog_config = cog_config
        self._logger = logger
        self._disable_debug_extra_init = disable_debug_extra_init
        self._unloaded_extensions = list[str]()

    @property
    def production(self) -> bool:
        return self._production

    @property
    def config(self) -> "Config":
        return self._config

    @property
    def cog_config(self) -> "CogConfig":
        return self._cog_config

    @property
    def logger(self) -> "Logger":
        return self._logger

    @property
    def disable_debug_extra_init(self) -> bool:
        return self._disable_debug_extra_init

    @property
    def unloaded_extensions(self) -> list[str]:
        return self._unloaded_extensions

    def _try_extension(self, operation: "Callable", name: str, *, package: str | None = None):
        logger = self._logger

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
            logger.exception(f"Extension '{name}' failed to load", exc_info=e)

    def load_extension(self, name: str, *, package: str | None = None) -> None:
        self._logger.info(f"Loading extension '{name}'")
        self._try_extension(super().load_extension, name, package=package)

    def load_extensions(self, path: str) -> None:
        if not (path_ := Path(path).resolve()).exists():
            return self._logger.warning(f"Path '{path_}' does not exist. Skip loading extension from this path")

        self._logger.info(f"Loading extensions from '{path_}'")
        super().load_extensions(path)

    def reload_extension(self, name: str, *, package: str | None = None) -> None:
        self._logger.info(f"Reloading extension '{name}'")
        self._try_extension(super().reload_extension, name, package=package)

    def unload_extension(self, name: str, *, package: str | None = None) -> None:
        self._logger.info(f"Unloading extension '{name}'")
        self._unloaded_extensions.append(name)
        self._try_extension(super().unload_extension, name, package=package)

    def init(self) -> "Self":
        logger = self._logger
        logger.info("Start initialization.")
        bot.set(self)
        self.load_extensions(self._config.extension_directory)
        logger.info("Finish initialization.")

        if not (self._production or self._disable_debug_extra_init):
            logger.info("Detected that 'debug extra initialization' is not disabled.")
            logger.info("Start debug extra initialization.")
            logger.info(f"Add '{Development.__name__}' cog")
            self.add_cog(Development())
            logger.info("Finish debug extra initialization.")
            logger.info("You can disable this behavior by passing '--disable-debug-extra-init' at startup")
        return self

    def run(self, *args: "Any", **kwargs: "Any") -> None:
        if not (token := env.get().get_bot_token()):
            self._logger.error("No bot token provided.")
            raise ValueError("No bot token provided.")
        return super().run(token, *args, **kwargs)

    async def on_ready(self) -> None:
        self._logger.info("The bot is ready")
        self._logger.info(f"User: {self.user}")
        self._logger.info(f"User ID: {self.user.id}")

    async def on_application_command(self, inter: "AppCmdInter"):
        interaction.set(inter)
        await self.process_application_commands(inter)
