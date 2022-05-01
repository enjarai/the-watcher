import logging
from functools import partial
from os import path
import os
import glob

import nextcord
from litematica_tools import MaterialList
from nextcord.ext import commands
from nextcord.ui import Button


class MaterialListView(nextcord.ui.View):
    def __init__(self, name, mat_list, *, timeout=180, blocks=True, entities=True, inventories=False):
        super().__init__(timeout=timeout)
        self.opts = {"Blocks": blocks, "Entities": entities, "Inventories": inventories}
        self.name = name
        self.mat_list = mat_list

        for opt in self.opts:
            self.add_toggle(opt, opt, self.toggle)

    async def on_timeout(self):
        await self.message.edit(view=None)

    def add_toggle(self, label, opt, callback):
        item = Button(
            label=label,
            style=self.get_toggled_style(self.opts[opt])
        )
        item.opt = opt
        item.callback = partial(callback, self, item)
        item._view = self
        # setattr(self, callback.__name__, item) # not sure if I need this, but it's here in case everything breaks
        self.children.append(item)

    async def toggle(self, view, button, interaction):
        toggle = not self.opts[button.opt]
        self.opts[button.opt] = toggle
        button.style = self.get_toggled_style(toggle)
        await self.update(interaction)

    async def update(self, interaction):
        embed = Litematics.get_material_list_embed(self.name, self.mat_list, self.opts)
        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="Delete", style=nextcord.ButtonStyle.danger)
    async def delete(self, button, interaction):
        await interaction.message.delete()
        self.stop()

    @staticmethod
    def get_toggled_style(active):
        return nextcord.ButtonStyle.primary if active else nextcord.ButtonStyle.secondary


class Litematics(commands.Cog):

    def __init__(self, bot):
        self.LOGGER = logging.getLogger('litematics')

        self.bot = bot
        self.clear_schems()

    def schems_path(self):
        schems = path.join(self.bot.CONFIG['temp_directory'], 'schematics/')
        os.makedirs(schems, exist_ok=True)
        return schems

    def clear_schems(self):
        files = glob.glob(path.join(self.schems_path(), '*'))
        for f in files:
            os.remove(f)

    @nextcord.slash_command(name="ping", description="test")
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("pong lmao")

    @nextcord.message_command(name="Parse Schematic")
    async def parse_command(self, interaction: nextcord.Interaction, message: nextcord.Message):
        for attachment in message.attachments:

            # Check file extension for compatibility
            if attachment.filename.endswith('.litematic'):  # TODO update to work with all types

                # File is valid, so defer the response
                await interaction.response.defer()
                self.LOGGER.info(f'Downloading and parsing {attachment.filename}')

                # Download the file, unless we have it cached
                file = path.join(self.schems_path(), f'{message.id}.litematic')
                if path.isfile(file):
                    self.LOGGER.info('  File cached, skipping download...')
                else:
                    self.LOGGER.info('  Downloading...')
                    await attachment.save(file)

                # Delegate the actual parsing to litematica_tools
                self.LOGGER.info('  Parsing...')
                mat_list = MaterialList.from_file(file)

                # Create the View object and send a response
                self.LOGGER.info('  Sending response...')
                view = MaterialListView(attachment.filename, mat_list)
                try:
                    view.message = await interaction.followup.send(
                        embed=self.get_material_list_embed(attachment.filename, mat_list, view.opts), view=view)
                except nextcord.errors.HTTPException:
                    await interaction.followup.send('Material list too large for discord to handle, aborted.')

                # Return if successful, breaking the for loop
                self.LOGGER.info('  Done.')
                return

        # Reply with error if all attachments are invalid
        await interaction.response.send_message('This message does not contain a supported schematic.', ephemeral=True)

    @staticmethod
    def get_material_list_embed(name, mat_list, opts):

        # Compose the list by checking the pressed buttons
        list_items = mat_list.composite_list(
            blocks=opts["Blocks"],
            items=opts["Inventories"],
            entities=opts["Entities"]
        ).sort().localise()

        max_name_len = max([len(i) for i in [*list_items.keys(), '']])
        max_amount_len = max([len(str(i)) for i in [*list_items.values(), '']])

        list_stacks = list_items.get_stacks()
        formatted = ''
        for k, v in list_items.items():
            formatted += '{}: {}{} {}{}\n'.format(
                k,
                ' ' * (max_name_len - len(k)),
                v,
                ' ' * (max_amount_len - len(str(v))),
                list_stacks[k]
            )
        embed = nextcord.Embed(title=name, description=f"```{formatted if formatted else 'Empty'}```")
        return embed


def setup(bot):
    bot.add_cog(Litematics(bot))
