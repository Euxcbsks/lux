from functools import cached_property
from inspect import signature
from typing import get_type_hints

from disnake.ext.commands import Cog

from .context_var import bot


class GeneralCog(Cog):
    def __init__(self) -> None:
        super().__init__()
        self._bot = bot.get()
        self._config_data = self._bot.cog_config.get_data(self.__class__.__name__)
        self.logger = self._bot.logger.getChild(self.__class__.__name__)

    @cached_property
    def config(self):
        if not (config_type := get_type_hints(self).get("config")):
            return self._config_data

        config_data = self._config_data.copy()
        missing = signature(config_type).parameters.keys() - self._config_data.keys()
        config_data |= {name: value for name in missing if (value := self._bot.cog_config.find(name)) is not None}

        try:
            return config_type(**config_data)
        except Exception as e:
            self.logger.exception(f"Failed while converting config data to '{config_type}'.", exc_info=e)
            raise e

    @property
    def bot(self):
        return self._bot
