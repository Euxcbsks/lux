from functools import cached_property

from disnake.ext.commands import Cog

from .context_var import bot


class GeneralCog(Cog):
    __CONFIG_TYPE = dict

    def __init__(self) -> None:
        super().__init__()
        self._bot = bot.get()
        self._config_data = self._bot.cog_config.get_data(self.__class__.__name__)

    @cached_property
    def config(self):
        return self.__CONFIG_TYPE(self._config_data)

    @property
    def bot(self):
        return self._bot
