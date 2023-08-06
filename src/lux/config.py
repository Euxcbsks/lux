from enum import StrEnum
from pathlib import Path
from tomllib import load
from typing import TYPE_CHECKING

from .context_var import is_production

if TYPE_CHECKING:
    from typing import Any, Self

DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_COG_CONFIG_PATH = Path("cog_config.toml")
DEFAULT_EXTENSION_DIRECTORY = "extension"


class _BotConfigKey(StrEnum):
    EXTENSION_DIRECTORY = "extension_directory"
    TEST_GUILDS = "test_guilds"


class Config:
    def __init__(self, data: "dict[str, Any]") -> None:
        self._all_data = data
        self._mode_data: "dict[str, Any]" = self._all_data[
            "production" if is_production.get() else "development"
        ]
        self._extension_directory: str = self._all_data.get(
            _BotConfigKey.EXTENSION_DIRECTORY,
            self._mode_data[_BotConfigKey.EXTENSION_DIRECTORY],
        )
        self._test_guilds: list[int] = self._all_data.get(
            _BotConfigKey.TEST_GUILDS, []
        ) + self._mode_data.get(_BotConfigKey.TEST_GUILDS, [])

    @property
    def extension_directory(self) -> str:
        return self._extension_directory

    @property
    def test_guilds(self) -> list[int]:
        return self._test_guilds

    @classmethod
    def default(cls) -> "Self":
        # TODO: Add default config values
        return cls(
            {
                "development": {
                    _BotConfigKey.EXTENSION_DIRECTORY: DEFAULT_EXTENSION_DIRECTORY,
                    _BotConfigKey.TEST_GUILDS: [],
                },
                "production": {
                    _BotConfigKey.EXTENSION_DIRECTORY: DEFAULT_EXTENSION_DIRECTORY
                },
            }
        )

    @classmethod
    def load_from_path(cls, path: Path) -> "Self":
        with path.open("rb") as f:
            return cls(load(f))


class CogConfig:
    def __init__(self, data: "dict[str, Any]") -> None:
        self._all_data = data

    def get_data(self, cog_name: str) -> "dict[str, Any]":
        return self._all_data.get(cog_name, {})

    @classmethod
    def default(cls) -> "Self":
        return cls({})

    @classmethod
    def load_from_path(cls, path: Path) -> "Self":
        with path.open("rb") as f:
            return cls(load(f))
