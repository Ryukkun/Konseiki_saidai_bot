import asyncio
import re
import os
from glob import glob
from pathlib import Path
from discord import ui, Interaction, SelectOption ,ButtonStyle, Embed, Guild, Colour, Message

from config import Config


# Button
class CreateView(ui.View):
    def __init__(self, play_def, page= 1):
        super().__init__(timeout=None)
        self.play_def = play_def

        voice_files = glob(f'{Config.voice_dir}*')
        self.split_voice_files = []
        while 25 < len(voice_files):
            self.split_voice_files.append(voice_files[:25])
            del voice_files[:25]
        if voice_files:
            self.split_voice_files.append(voice_files)

        self.select = CreateSelect(page, self)
        self.select2 = CreateSelect2(page, self)
        self.add_item(self.select)
        self.add_item(self.select2)
        self.add_item(CreateButtonPlay(self))
        self.add_item(CreateButtonRefresh(self))
        self.add_item(CreateButtonVoiceDel(self))
        self.add_item(CreateButtonMessageDel())




class CreateSelect(ui.Select):
    def __init__(self, page, parent:'CreateView') -> None:
        self.parent = parent
        select_opt:list[SelectOption] = []

        for _ in range(len(parent.split_voice_files)):
            _ += 1
            select_opt.append(SelectOption(label=f'Page : {_}', value=_, default=False))
        select_opt[page-1].default = True

        super().__init__(placeholder='ページ数', options=select_opt, row=0)


    async def callback(self, interaction: Interaction):
        loop = asyncio.get_event_loop()
        loop.create_task(interaction.response.defer())
        await interaction.message.edit(view=CreateView(play_def=self.parent.play_def, page=self.values[0]))



class CreateSelect2(ui.Select):
    def __init__(self, page, parent:'CreateView') -> None:

        select_opt = [SelectOption(label=Path(_).stem, value=_) for _ in parent.split_voice_files[page-1]]
        select_opt[0].default = True
        self.voice_res = select_opt[0].value
        super().__init__(placeholder='今世紀最大ファイル', options=select_opt, row=2)


    async def callback(self, interaction: Interaction):
        self.voice_res = self.values[0]
        await interaction.response.defer()


class CreateButtonPlay(ui.Button):
    def __init__(self, parent:'CreateView') -> None:
        self.parent = parent
        super().__init__(label='Play', style=ButtonStyle.blurple, row=3)


    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        await self.parent.play_def(interaction, self.parent.select2.voice_res)



class CreateButtonRefresh(ui.Button):
    def __init__(self, parent:'CreateView') -> None:
        self.parent = parent
        super().__init__(label='↺', style=ButtonStyle.blurple, row=3)

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(view=CreateView(self.parent.play_def))



class CreateButtonVoiceDel(ui.Button):
    def __init__(self, parent:'CreateView') -> None:
        self.parent = parent
        super().__init__(label='音声消去', style=ButtonStyle.red, row=3)

    async def callback(self, interaction: Interaction):
        if interaction.permissions.administrator:
            voice = self.parent.select2.voice_res
            view = ui.View(timeout=None)
            view.add_item(VoiceDelYes(voice= voice, message= interaction.message, play_def= self.parent.play_def))
            await interaction.response.send_message(embed=Embed(title='本当に削除してもいいのかい どっちなんだい！',description=f'ファイル名 : {Path(voice).stem}', colour=Colour.yellow()), view=view, ephemeral=True)
        else:
            await interaction.response.send_message(embed=Embed(title='この操作には管理者権限が必要です ;w;', colour=Colour.dark_gray()), ephemeral=True)


class VoiceDelYes(ui.Button):
    def __init__(self, voice, message:Message, play_def):
        self.voice = voice
        self.message = message
        self.play_def = play_def
        super().__init__(label='はい', style=ButtonStyle.green, row=0)

    async def callback(self, interaction: Interaction):
        if os.path.isfile(self.voice):
            os.remove(self.voice)
            await interaction.response.send_message(embed=Embed(title='削除完了 =)',description='*これらのメッセージは消していいよん', colour=Colour.dark_gray()), ephemeral=True)
            await self.message.edit(view=CreateView(self.play_def))
        else:
            await interaction.response.defer()


class CreateButtonMessageDel(ui.Button):
    def __init__(self) -> None:
        super().__init__(label='メッセージ消去', style=ButtonStyle.red, row=3)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        await interaction.message.delete()