from logging import DEBUG
from pathlib import Path as PathType

from click import Path, command, option

from .bot import Lux
from .config import DEFAULT_COG_CONFIG_PATH, DEFAULT_CONFIG_PATH, CogConfig, Config
from .context_var import env as env_var
from .context_var import is_production as is_production_var
from .env import Env
from .logger import default_logger

try:
    import dotenv  # type: ignore
except ImportError:
    dotenv = None


is_production = option(
    "-P",
    "--production",
    "is_production",
    is_flag=True,
    default=False,
    show_default=True,
)
config_path = option(
    "-C",
    "--config",
    "config_path",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=DEFAULT_CONFIG_PATH,
    show_default=True,
)
cog_config_path = option(
    "-CF",
    "--cog-config",
    "cog_config_path",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=DEFAULT_COG_CONFIG_PATH,
    show_default=True,
)
env_path = option(
    "-E",
    "--env",
    "env_path",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=PathType(".env"),
    show_default=True,
)
disable_debug_extra_init = option(
    "--disable-debug-extra-init",
    "disable_debug_extra_init",
    is_flag=True,
    default=False,
    show_default=True,
)


def process_is_production(is_production: bool):
    if not is_production:
        default_logger.setLevel(DEBUG)

    default_logger.info(f"Running in {'production' if is_production else 'debug'} mode.")
    is_production_var.set(is_production)
    return is_production


def process_config_path(config_path: PathType) -> Config:
    if not config_path.exists():
        default_logger.warning(f"File '{config_path}' does not exist.")
        return Config.default()
    else:
        default_logger.info(f"Using config file '{config_path}'.")
        return Config.load_from_path(config_path)


def process_cog_config_path(cog_config_path: PathType) -> CogConfig:
    if cog_config_path.exists():
        default_logger.info(f"Using cog config file '{cog_config_path}'.")
        return CogConfig.load_from_path(cog_config_path)
    default_logger.warning(f"File '{cog_config_path}' does not exist.")
    return CogConfig.default()


def process_env_path(env_path: PathType) -> None:
    if not env_path.exists():
        default_logger.warning(f"File '{env_path}' does not exist.")
    elif not dotenv:
        default_logger.warning(
            "'python-dotenv' is not installed. Skip loading .env file."
        )
    else:
        default_logger.info(f"Using .env file '{env_path}'.")
        dotenv.load_dotenv(env_path)

    env_var.set(Env())


@command
@is_production
@config_path
@cog_config_path
@env_path
@disable_debug_extra_init
def default_entry(
    is_production: bool,
    config_path: PathType,
    cog_config_path: PathType,
    env_path: PathType,
    disable_debug_extra_init: bool,
) -> None:
    production = process_is_production(is_production)
    config = process_config_path(config_path)
    cog_config = process_cog_config_path(cog_config_path)
    process_env_path(env_path)

    Lux(
        production=production,
        config=config,
        cog_config=cog_config,
        disable_debug_extra_init=disable_debug_extra_init,
    ).init().run()
