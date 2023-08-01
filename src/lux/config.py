from enum import StrEnum
from tomllib import load
from typing import TYPE_CHECKING

from .context_var import mode

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, Self

DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_COG_CONFIG_PATH = Path("cog_config.toml")


class _ConfigKey(StrEnum):
    EXTENSION_DIRECTORY = "extension_directory"
    TEST_GUILDS = "test_guilds"


class Config:
    def __init__(self, data: "dict[str, Any]") -> None:
        self._all_data = data
        self._mode_data: "dict[str, Any]" = self._all_data[mode.get().name.lower()]
        self._extension_directory: str = self._all_data.get(
            _ConfigKey.EXTENSION_DIRECTORY,
            self._mode_data[_ConfigKey.EXTENSION_DIRECTORY],
        )
        self._test_guilds: list[int] = self._all_data.get(
            _ConfigKey.TEST_GUILDS, []
        ) + self._mode_data.get(_ConfigKey.TEST_GUILDS, [])

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
                    _ConfigKey.EXTENSION_DIRECTORY: "extension",
                    _ConfigKey.TEST_GUILDS: [],
                },
                "production": {_ConfigKey.EXTENSION_DIRECTORY: "extension"},
            }
        )

    @classmethod
    def load_from_path(cls, path: "Path") -> "Self":
        with path.open("rb") as f:
            return cls(load(f))


class CogConfig:
    def __init__(self, data: "dict[str, Any]") -> None:
        self._all_data = data

    @classmethod
    def default(cls) -> "Self":
        return cls({})

    @classmethod
    def load_from_path(cls, path: "Path") -> "Self":
        with path.open("rb") as f:
            return cls(load(f))
