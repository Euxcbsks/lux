from enum import StrEnum
from functools import cached_property
from pathlib import Path
from tomllib import TOMLDecodeError, load
from typing import Any, Self, TypeVar, overload

from disnake import Intents
from pydantic import Field, TypeAdapter, ValidationError
from pydantic.dataclasses import dataclass

from .context_var import is_production
from .logger import default_logger

# For type hint
_DEFAULT_TYPE = TypeVar("_DEFAULT_TYPE")

DEFAULT_BOT_CONFIG_PATH = Path("bot_config.toml")
DEFAULT_COG_CONFIG_PATH = Path("cog_config.toml")
DEFAULT_EXTENSION_DIRECTORY = "extension"


class RootConfigKey(StrEnum):
    GLOBAL = "GLOBAL"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class BotConfigKey(StrEnum):
    EXTENSION_DIRECTORY = "extension_directory"
    TEST_GUILDS = "test_guilds"
    INTENT_TYPE = "intent_type"
    INTENT_FLAG = "intent_flag"


DEFAULT_RAW_ROOT_DATA = {RootConfigKey.GLOBAL: {}, RootConfigKey.PRODUCTION: {}, RootConfigKey.DEVELOPMENT: {}}
RootConfigDataType = dict[RootConfigKey, dict[str, Any]]
RootConfigDataValidator = TypeAdapter(RootConfigDataType)
ListOfIntValidator = TypeAdapter(list[int])
DictOfStrAnyValidator = TypeAdapter(dict[str, Any])
DictOfStrBoolValidator = TypeAdapter(dict[str, bool])


@dataclass(frozen=True)
class RootConfigData:
    all: RootConfigDataType = Field(default_factory=lambda: DEFAULT_RAW_ROOT_DATA)

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

    @property
    def root_global(self) -> dict[str, Any]:
        return self.all.get(RootConfigKey.GLOBAL, {})

    @property
    def development(self) -> dict[str, Any]:
        return self.all.get(RootConfigKey.DEVELOPMENT, {})

    @property
    def production(self) -> dict[str, Any]:
        return self.all.get(RootConfigKey.PRODUCTION, {})

    @property
    def mode(self) -> dict[str, Any]:
        return self.production if is_production.get() else self.development

    @overload
    def find(self, key: str) -> Any | None:
        ...

    @overload
    def find(self, key: str, default: _DEFAULT_TYPE = None) -> Any | _DEFAULT_TYPE:
        ...

    def find(self, key: str, default: Any = None) -> Any:
        return self.mode.get(key, self.root_global.get(key, default))

    @overload
    def find_all(self, key: str) -> tuple[Any | None, Any | None]:
        ...

    @overload
    def find_all(self, key: str, default: _DEFAULT_TYPE = None) -> tuple[Any | _DEFAULT_TYPE, Any | _DEFAULT_TYPE]:
        ...

    def find_all(self, key: str, default: Any = None) -> tuple[Any, Any]:
        return self.mode.get(key, default), self.root_global.get(key, default)


class BotConfig:
    def __init__(self, data: RootConfigData) -> None:
        self._data = data

    @classmethod
    def default(cls) -> Self:
        data = DEFAULT_RAW_ROOT_DATA.copy() | {
            RootConfigKey.DEVELOPMENT: {
                BotConfigKey.EXTENSION_DIRECTORY: DEFAULT_EXTENSION_DIRECTORY,
                BotConfigKey.TEST_GUILDS: [],
            },
            RootConfigKey.PRODUCTION: {BotConfigKey.EXTENSION_DIRECTORY: DEFAULT_EXTENSION_DIRECTORY},
        }
        return cls(RootConfigData(RootConfigDataValidator.validate_python(data)))

    @classmethod
    def load_from_path(cls, path: Path) -> Self:
        return cls(RootConfigData.load_from_path(path))

    @property
    def extension_directory(self) -> str:
        return str(self._data.find(BotConfigKey.EXTENSION_DIRECTORY, DEFAULT_EXTENSION_DIRECTORY))

    @cached_property
    def test_guilds(self) -> list[int]:
        result = []
        for _ in self._data.find_all(BotConfigKey.TEST_GUILDS, []):
            result.extend(_)

        try:
            return ListOfIntValidator.validate_python(result)
        except ValidationError as e:
            default_logger.exception(
                f"Failed while validation bot config data '{BotConfigKey.TEST_GUILDS}'.", exc_info=e
            )
            raise e

    @cached_property
    def intents(self) -> Intents:
        intent_type = str(self._data.find(BotConfigKey.INTENT_TYPE, Intents.default.__name__))

        if intent_type not in [Intents.default.__name__, Intents.all.__name__, Intents.none.__name__]:
            message = f"Invalid intent type '{intent_type}'."
            default_logger.error(message)
            raise ValueError(message)

        intent: Intents = getattr(Intents, intent_type)()

        if not (intent_flag := DictOfStrBoolValidator.validate_python(self._data.find(BotConfigKey.INTENT_FLAG, {}))):
            return intent

        try:
            intent_modify = Intents(**intent_flag)
        except TypeError as e:
            default_logger.exception(str(e), exc_info=e)
            raise e

        return intent | intent_modify


class CogConfig:
    def __init__(self, data: RootConfigData) -> None:
        self._data = data

    @classmethod
    def default(cls) -> Self:
        return cls(RootConfigData())

    @classmethod
    def load_from_path(cls, path: Path) -> Self:
        return cls(RootConfigData.load_from_path(path))

    @cached_property
    def mode_global(self) -> dict[str, Any]:
        data = self._data.mode.get(RootConfigKey.GLOBAL, {})

        try:
            return DictOfStrAnyValidator.validate_python(data)
        except ValidationError as e:
            mode = RootConfigKey.PRODUCTION if is_production.get() else RootConfigKey.DEVELOPMENT
            default_logger.exception(f"Failed while validation mode({mode}) global cog config data.", exc_info=e)
            raise e

    def get_data(self, cog_name: str) -> dict[str, Any]:
        data = self._data.find(cog_name, {})

        try:
            return DictOfStrAnyValidator.validate_python(data)
        except ValidationError as e:
            default_logger.exception(f"Failed while validation cog config data '{cog_name}'.", exc_info=e)
            raise e

    @overload
    def find(self, key: str, /) -> Any | None:
        ...

    @overload
    def find(self, key: str, default: _DEFAULT_TYPE = None, /) -> Any | _DEFAULT_TYPE:
        ...

    def find(self, key: str, default: Any = None, /) -> Any:
        return self._data.mode.get(key, self.mode_global.get(key, self._data.root_global.get(key, default)))

    @overload
    def find_all(self, key: str) -> tuple[Any | None, Any | None, Any | None]:
        ...

    @overload
    def find_all(
        self, key: str, default: _DEFAULT_TYPE = None
    ) -> tuple[Any | _DEFAULT_TYPE, Any | _DEFAULT_TYPE, Any | _DEFAULT_TYPE]:
        ...

    def find_all(self, key: str, default: Any = None) -> tuple[Any, Any, Any]:
        return (
            self._data.mode.get(key, default),
            self.mode_global.get(key, default),
            self._data.root_global.get(key, default),
        )
