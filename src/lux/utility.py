from typing import TYPE_CHECKING

from disnake.utils import MISSING

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
