from functools import partial

from .context_var import interaction

partial(interaction.get().send, ephemeral=True)
