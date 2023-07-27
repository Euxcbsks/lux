from typing import TYPE_CHECKING

from disnake import AppCmdInter
from disnake.ext.commands import Param, slash_command
from disnake.utils import MISSING

from .auto_complete import loaded_extension, unloaded_extension
from .cog import GeneralCog
from .context_var import interaction

if TYPE_CHECKING:
    from disnake import AllowedMentions, Embed, File, MessageFlags
    from disnake.ui import Components, MessageUIComponent, View


async def send_ephemeral(
    content: str | None = None,
    *,
    embed: "Embed" = MISSING,
    embeds: "list[Embed]" = MISSING,
    file: "File" = MISSING,
    files: "list[File]" = MISSING,
    allowed_mentions: "AllowedMentions" = MISSING,
    view: "View" = MISSING,
    components: "Components[MessageUIComponent]" = MISSING,
    tts: bool = False,
    suppress_embeds: bool = MISSING,
    flags: "MessageFlags" = MISSING,
    delete_after: float = MISSING,
):
    """Same as `disnake.interaction.application_command.ApplicationCommandInteraction.send` but set `ephemeral` to `True`"""
    await interaction.get().send(
        content,
        embed=embed,
        embeds=embeds,
        file=file,
        files=files,
        allowed_mentions=allowed_mentions,
        view=view,
        components=components,
        tts=tts,
        ephemeral=True,
        suppress_embeds=suppress_embeds,
        flags=flags,
        delete_after=delete_after,
    )


class Development(GeneralCog):
    """A cog containing some convenience commands for development"""

    @slash_command()
    async def extension(self, inter: AppCmdInter):
        return None

    @extension.sub_command()
    async def load(
        self, inter: AppCmdInter, name: str = Param(autocomplete=unloaded_extension)
    ):
        self.bot._logger.debug(f"Loading extension '{name}'")
        self.bot.load_extension(name)
        await send_ephemeral(f"Loaded extension `{name}`")

    @extension.sub_command()
    async def reload(
        self, inter: AppCmdInter, name: str = Param(autocomplete=loaded_extension)
    ):
        self.bot._logger.debug(f"Reloading extension '{name}'")
        self.bot.reload_extension(name)
        await send_ephemeral(f"Reloaded extension `{name}`")

    @extension.sub_command()
    async def unload(
        self, inter: AppCmdInter, name: str = Param(autocomplete=loaded_extension)
    ):
        self.bot._logger.debug(f"Unloading extension '{name}'")
        self.bot.unload_extension(name)
        await send_ephemeral(f"Unloaded extension `{name}`")
