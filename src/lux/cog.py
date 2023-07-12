from disnake.ext.commands import Cog

from .context_var import bot


class GeneralCog(Cog):
    def __init__(self) -> None:
        super().__init__()
        self._bot = bot.get()

    @property
    def bot(self):
        return self._bot
