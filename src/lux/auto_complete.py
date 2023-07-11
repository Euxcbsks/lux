from typing import TYPE_CHECKING

from .context_var import bot

if TYPE_CHECKING:
    from typing import Iterable, Mapping


def list_(iterable: "Iterable[str]", user_input: str | None):
    if not user_input:
        return list(iterable)
    return [element for element in iterable if user_input.lower() in element]


def dict_(mapping: "Mapping[str, str]", user_input: str | None):
    if not user_input:
        return dict(mapping)
    return {key: value for key, value in mapping.items() if user_input.lower() in key}


def extension(user_input: str | None = None):
    names = bot.get().cogs.keys()

    if not user_input:
        return list(names)
    return list_(names, user_input)
