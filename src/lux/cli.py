from pathlib import Path as PathType

from click import Choice, Path, command, option

from .bot import Lux
from .config import Config
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
config = option(
    "-C",
    "--config",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=PathType("config.toml"),
    show_default=True,
)
env = option(
    "-E",
    "--env",
    type=Path(dir_okay=False, resolve_path=True, path_type=PathType),
    default=PathType(".env"),
    show_default=True,
)


def process_mode(mode: str):
    if (mode_ := Modes(mode.lower())).is_dev():
        from logging import DEBUG

        default_logger.setLevel(DEBUG)

    mode_var.set(mode_.fullname)
    default_logger.info(f"Running in '{mode}' mode.")
    return mode_


def process_config(config_path: PathType):
    if not config_path.exists():
        default_logger.warning(f"File '{config_path}' does not exist.")
        return Config.default()
    else:
        default_logger.info(f"Using config file '{config_path}'.")
        return Config.load_from_path(config_path)


def process_env(env_path: PathType):
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
@config
@env
def default_entry(mode: str, config: PathType, env: PathType):
    mode_ = process_mode(mode)
    config_ = process_config(config)
    process_env(env)
    Lux(mode=mode_, config=config_).init().run()
