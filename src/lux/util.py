from functools import partial

from .context_var import interaction

send_ephemeral = partial(interaction.get().send, ephemeral=True)
