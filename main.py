import discord
import os
import re
import shutil
import asyncio
import logging
import random
from glob import glob
from pathlib import Path
from discord.ext import commands
from typing import Dict

_my_dir = Path(__file__).parent
os.chdir(str(_my_dir))

####  Config
config_path = str(_my_dir / 'config.py')
temp_config_path = str(_my_dir / 'pi_yo_6' / 'template' / '_config.py')
try:
    from config import Config
except Exception:
    shutil.copyfile(temp_config_path, config_path)
    from config import Config

from voice_client import MultiAudio
from cm_list import CreateView
from audio_source import StreamAudioData as SAD

os.makedirs(Config.voice_dir, exist_ok=True)



####  起動準備 And 初期設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix=Config.prefix, strip_after_prefix=True, intents=intents)
g_opts:Dict[int, 'DataInfo'] = {}




####  基本的コマンド
@client.event
async def on_ready():
    print('Logged in')
    print(client.user.name)
    print(client.user.id)
    print('----------------')
    


@client.command()
async def join(ctx:commands.Context):
    if vc := ctx.author.voice:
        print(f'{ctx.guild.name} : #join')
        await _join(channel=vc.channel, guild=ctx.guild)
        return True

async def _join(channel:discord.VoiceChannel, guild:discord.Guild):
    try: await channel.connect(self_deaf=True)
    except discord.ClientException: return
    g_opts[guild.id] = DataInfo(guild)


@client.command()
async def bye(ctx:commands.Context):
    guild = ctx.guild
    vc = guild.voice_client
    if vc:
        print(f'{guild.name} : #切断')
        await _bye(guild)


async def _bye(guild:discord.Guild):
    gid = guild.id
    vc = guild.voice_client

    g_opts[gid].MA.kill()
    del g_opts[gid]
    
    await asyncio.sleep(0.1)
    try: await vc.disconnect()
    except Exception: pass


@client.command()
async def add(ctx:commands.Context, name):

    reply = ctx.reply
    if not ctx.message.attachments:
        await reply(embed=discord.Embed(title='ファイルを添付してから出直してきてね ;w;',colour=discord.Colour.dark_grey()) ,delete_after=10.0)
        return

    file = ctx.message.attachments[0]
    if not '.' in name:
        ext = re.match(r'.*(\..+?$)',file.filename).group(1)
        name += ext
    path = Path(f'{Config.voice_dir}{name}').resolve()
    
    try:
        await file.save(path)
    except Exception:
        await reply(embed=discord.Embed(title='保存に失敗しました ;w;',colour=discord.Colour.dark_grey()) ,delete_after=10.0)
    else:
        await reply(embed=discord.Embed(title='保存に成功しました =)',colour=discord.Colour.dark_grey()) ,delete_after=10.0)


@client.command()
async def list(ctx:commands.Context):
    await ctx.send(view=CreateView(play_konseiki_from_interaction))

#---------------------------------


@client.event
async def on_message(message:discord.Message):
    guild = message.guild
    if not guild: return
    gid = message.guild.id
    voice = message.author.voice

    # 発言者がチャンネルに入っているか 
    # 発言者がBotの場合はPass
    # 今世紀最大検知
    if message.author.voice and not message.author.bot and '今世紀最大' in message.content:
        
        print(f'\n#今世紀最大 検知！  : {guild.name} ({message.channel.name})')
        print( message.author.name +" (",message.author.display_name,') : '+ message.content)

        if voice.channel and not guild.voice_client:
            await join(message)

        try:
            text = message.content
            count = 0
            while '今世紀最大' in text:
                text = text.replace('今世紀最大', '', 1)
                if count != 0:
                    await asyncio.sleep(0.1)
                await g_opts[gid].play_konseiki()
                count += 1
                if count == 10 : break
        except KeyError:pass

    # Fin
    await client.process_commands(message)



async def play_konseiki_from_interaction(interaction:discord.Interaction, source= None):
    gid = interaction.guild_id

    if interaction.user.voice:
        if not interaction.guild.voice_client:
            await _join(channel=interaction.user.voice.channel, guild=interaction.guild)
        
        await g_opts[gid].play_konseiki(source=source)


class DataInfo:
    def __init__(self, guild:discord.Guild):
        self.guild = guild
        self.gn = guild.name
        self.gid = guild.id
        self.vc = guild.voice_client
        self.MA = MultiAudio(guild, client, self)
        self.loop = client.loop
        self.client = client


    async def play_konseiki(self, source= None):
        Vvc = self.MA.add_player(opus=False)
        if not source:
            source = random.choice(glob(f'{Config.voice_dir}*'))

        await Vvc.play(SAD(source).Url_Only(), lambda : self.loop.create_task(self.finish(Vvc)))


    async def finish(self, Vvc):
        self.MA.Players.remove(Vvc)

        if self.MA.Players:
            return
        await asyncio.sleep(1.0)
        if not self.MA.Players:
            await _bye(self.guild)


client.run(Config.token, log_level=logging.WARNING)