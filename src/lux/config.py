from enum import StrEnum
from functools import cached_property
from pathlib import Path
from tomllib import TOMLDecodeError, load
from typing import Any, Self, TypeVar, overload

from pydantic import Field, TypeAdapter, ValidationError
from pydantic.dataclasses import dataclass

from .context_var import is_production
from .logger import default_logger

# For type hint
_DEFAULT_TYPE = TypeVar("_DEFAULT_TYPE")

DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_COG_CONFIG_PATH = Path("cog_config.toml")
DEFAULT_EXTENSION_DIRECTORY = "extension"


class RootConfigKey(StrEnum):
    GLOBAL = "GLOBAL"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class _BotConfigKey(StrEnum):
    EXTENSION_DIRECTORY = "extension_directory"
    TEST_GUILDS = "test_guilds"


DEFAULT_RAW_ROOT_DATA = {RootConfigKey.GLOBAL: {}, RootConfigKey.PRODUCTION: {}, RootConfigKey.DEVELOPMENT: {}}
RootConfigDataType = dict[RootConfigKey, dict[str, Any]]
RootConfigDataValidator = TypeAdapter(RootConfigDataType)
ListOfIntValidator = TypeAdapter(list[int])
DictOfStrAnyValidator = TypeAdapter(dict[str, Any])


@dataclass(frozen=True)
class RootConfigData:
    all: RootConfigDataType = Field(default_factory=lambda: DEFAULT_RAW_ROOT_DATA)

    @property
    def global_(self) -> dict[str, Any]:
        return self.all.get(RootConfigKey.GLOBAL, {})

    @property
    def development(self):
        return self.all.get(RootConfigKey.DEVELOPMENT, {})

    @property
    def production(self):
        return self.all.get(RootConfigKey.PRODUCTION, {})

    @property
    def mode(self) -> dict[str, Any]:
        return self.production if is_production.get() else self.development

    @classmethod
    def load_from_path(cls, path: Path) -> Self:
        try:
            with path.open("rb") as file:
                data = load(file)
        except FileNotFoundError as e:
            default_logger.exception(f"File '{path.resolve()}' does not exists.", exc_info=e)
            raise e
        except TOMLDecodeError as e:
            default_logger.exception(f"Failed while load config data from path '{path.resolve()}'", exc_info=e)
            raise e

        try:
            return cls(RootConfigDataValidator.validate_python(data))
        except ValidationError as e:
            default_logger.exception("Failed while validation root config data structure", exc_info=e)
            raise e

    @overload
    def find(self, key: str) -> Any | None:
        ...

    @overload
    def find(self, key: str, default: _DEFAULT_TYPE = None) -> Any | _DEFAULT_TYPE:
        ...

    def find(self, key: str, default: Any = None) -> Any:
        return self.mode.get(key, self.global_.get(key, default))

    @overload
    def find_all(self, key: str) -> tuple[Any | None, Any | None]:
        ...

    @overload
    def find_all(self, key: str, default: _DEFAULT_TYPE = None) -> tuple[Any | _DEFAULT_TYPE, Any | _DEFAULT_TYPE]:
        ...

    def find_all(self, key: str, default: Any = None) -> tuple[Any, Any]:
        return self.mode.get(key, default), self.global_.get(key, default)


class Config:
    def __init__(self, data: RootConfigData) -> None:
        self._data = data

    @property
    def extension_directory(self) -> str:
        return str(self._data.find(_BotConfigKey.EXTENSION_DIRECTORY, DEFAULT_EXTENSION_DIRECTORY))

    @cached_property
    def test_guilds(self) -> list[int]:
        result = []
        for _ in self._data.find_all(_BotConfigKey.TEST_GUILDS, []):
            result.extend(_)

        try:
            return ListOfIntValidator.validate_python(result)
        except ValidationError as e:
            default_logger.exception(
                f"Failed while validation bot config data '{_BotConfigKey.TEST_GUILDS}'", exc_info=e
            )
            raise e

    @classmethod
    def default(cls) -> Self:
        data = DEFAULT_RAW_ROOT_DATA.copy() | {
            RootConfigKey.DEVELOPMENT: {
                _BotConfigKey.EXTENSION_DIRECTORY: DEFAULT_EXTENSION_DIRECTORY,
                _BotConfigKey.TEST_GUILDS: [],
            },
            RootConfigKey.PRODUCTION: {_BotConfigKey.EXTENSION_DIRECTORY: DEFAULT_EXTENSION_DIRECTORY},
        }
        return cls(RootConfigData(RootConfigDataValidator.validate_python(data)))

    @classmethod
    def load_from_path(cls, path: Path) -> Self:
        return cls(RootConfigData.load_from_path(path))


class CogConfig:
    def __init__(self, data: RootConfigData) -> None:
        self._data = data

    def get_data(self, cog_name: str) -> dict[str, Any]:
        data = self._data.find(cog_name, {})

        try:
            return DictOfStrAnyValidator.validate_python(data)
        except ValidationError as e:
            default_logger.exception(f"Failed while validation cog config data '{cog_name}'", exc_info=e)
            raise e

    @classmethod
    def default(cls):
        return cls(RootConfigData())

    @classmethod
    def load_from_path(cls, path: Path):
        return cls(RootConfigData.load_from_path(path))
