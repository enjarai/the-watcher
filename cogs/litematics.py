from functools import partial
from os import path

import nextcord.ui
from nextcord.ext import commands
from nextcord.ui import Button

import litematicparse


class MaterialListView(nextcord.ui.View):
    def __init__(self, name, region, *, timeout=180, blocks=True, entities=True, inventories=False):
        super().__init__(timeout=timeout)
        self.opts = {"Blocks": blocks, "Entities": entities, "Inventories": inventories}
        self.name = name
        self.region = region

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
        embed = Litematics.get_material_list_embed(self.name, self.region, self.opts)
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
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        for attachment in message.attachments:
            if attachment.filename.endswith('.litematic'):
                await message.channel.trigger_typing()
                print(f'Downloading and parsing {attachment.filename}')

                file = path.join(self.bot.CONFIG['temp_directory'], 'schematic.litematic')
                await attachment.save(file)

                schematic = litematicparse.Litematic(file)

                print(f'  Sending response')
                for name, region in schematic.regions.items():
                    view = MaterialListView(name, region)
                    view.message = await message.reply(
                        embed=self.get_material_list_embed(name, region, view.opts), view=view)

    @staticmethod
    def get_material_list_embed(name, region, opts):
        materials = (
            (region.block_count() if opts["Blocks"] else litematicparse.MaterialList()) +
            (region.entity_count() if opts["Entities"] else litematicparse.MaterialList()) +
            (region.inventory_count() if opts["Inventories"] else litematicparse.MaterialList())
        )
        formatted = str(materials)
        embed = nextcord.Embed(title=name, description=f"```{formatted if formatted else 'Empty'}```")
        return embed


def setup(bot):
    bot.add_cog(Litematics(bot))
