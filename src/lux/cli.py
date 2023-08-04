from pathlib import Path as PathType

from click import Choice, Path, command, option

from .bot import Lux
from .config import DEFAULT_COG_CONFIG_PATH, DEFAULT_CONFIG_PATH, CogConfig, Config
from .context_var import env as env_var
from .context_var import mode as mode_var
from .env import Env
from .logger import default_logger
from .mode import Modes

try:
    import dotenv  # type: ignore
except ImportError:
    dotenv = None


mode = option(
    "-M",
    "--mode",
    type=Choice(
        [str(mode.name) for mode in Modes],
        case_sensitive=False,
    ),
    default="dev",
    show_default=True,
)
config_path = option(
    "-C",
    "--config",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=DEFAULT_CONFIG_PATH,
    show_default=True,
)
cog_config_path = option(
    "-CF",
    "--cog-config",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=DEFAULT_COG_CONFIG_PATH,
    show_default=True,
)
env_path = option(
    "-E",
    "--env",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=PathType(".env"),
    show_default=True,
)
disable_debug_extra_init = option(
    "--disable-debug-extra-init",
    type=bool,
    default=False,
    show_default=True,
)


def process_mode(mode: str) -> Modes:
    if (mode_ := Modes(mode.lower())).is_dev():
        from logging import DEBUG

        default_logger.setLevel(DEBUG)

    mode_var.set(mode_.fullname)
    default_logger.info(f"Running in '{mode}' mode.")
    return mode_


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
            "'python-dotenv' is not installed. Skipping load .env file."
        )
    else:
        default_logger.info(f"Using .env file '{env_path}'.")
        dotenv.load_dotenv(env_path)

    env_var.set(Env())


@command
@mode
@config_path
@cog_config_path
@env_path
@disable_debug_extra_init
def default_entry(
    mode: str,
    config_path: PathType,
    cog_config_path: PathType,
    env_path: PathType,
    disable_debug_extra_init: bool,
) -> None:
    mode = process_mode(mode)
    config = process_config_path(config_path)
    cog_config = process_cog_config_path(cog_config_path)
    process_env_path(env_path)

    Lux(
        mode=mode,
        config=config,
        cog_config=cog_config,
        disable_debug_extra_init=disable_debug_extra_init,
    ).init().run()
