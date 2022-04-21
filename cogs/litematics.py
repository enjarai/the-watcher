from functools import partial
from os import path

import nextcord.ui
from nextcord.ext import commands
from nextcord.ui import Button

import litematica_tools


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
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        for attachment in message.attachments:
            if attachment.filename.endswith('.litematic'):
                await message.channel.trigger_typing()
                print(f'Downloading and parsing {attachment.filename}')

                file = path.join(self.bot.CONFIG['temp_directory'], 'schematic.litematic')
                await attachment.save(file)

                schematic = litematica_tools.schematic_parse.NBTFile(file)
                mat_list = litematica_tools.MaterialList(schematic)

                print(f'  Sending response')
                view = MaterialListView(attachment.filename, mat_list)
                view.message = await message.reply(
                    embed=self.get_material_list_embed(attachment.filename, mat_list, view.opts), view=view)

    @staticmethod
    def get_material_list_embed(name, mat_list, opts):
        list_items = mat_list.composite_list(
            blocks=opts["Blocks"],
            items=opts["Inventories"],
            entities=opts["Entities"]
        )
        formatted = ''
        for k, v in list_items.localise().items():
            formatted += f'{k}: {v}\n'
        embed = nextcord.Embed(title=name, description=f"```{formatted if formatted else 'Empty'}```")
        return embed


def setup(bot):
    bot.add_cog(Litematics(bot))
