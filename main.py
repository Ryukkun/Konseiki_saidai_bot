import discord
import os
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
from audio_source import StreamAudioData as SAD

os.makedirs(Config.voice_dir, exist_ok=True)



####  起動準備 And 初期設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix=Config.prefix,intents=intents)
g_opts:Dict[int, 'DataInfo'] = {}




####  基本的コマンド
@client.event
async def on_ready():
    print('Logged in')
    print(client.user.name)
    print(client.user.id)
    print('----------------')
    


@client.command()
async def play(ctx:commands.Context, count:int):
    print('ok')
    guild = ctx.guild
    if not guild: return
    gid = ctx.guild.id
    voice = ctx.author.voice

    # 読み上げ
    # 発言者がチャンネルに入っているか
    if not ctx.author.voice:
        return

    # # countが ちゃんと数字になるか！
    # try: count = int(count)
    # except Exception: return

    print(f'\n#今世紀最大 検知！ x{count} : {guild.name} ({ctx.channel.name})')
    print( ctx.author.name +" (",ctx.author.display_name,')')

    if voice.channel and not guild.voice_client:
        await join(ctx)

    try:
        for _ in range(count):
            await g_opts[gid].play_konseiki()
    except KeyError:pass

@client.command()
async def ts(ctx):
    print('ts')

@client.command()
async def join(ctx:commands.Context):
    if vc := ctx.author.voice:
        gid = ctx.guild.id
        print(f'{ctx.guild.name} : #join')
        try: await vc.channel.connect(self_deaf=True)
        except discord.ClientException: return
        g_opts[gid] = DataInfo(ctx.guild)
        return True


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



#---------------------------------


@client.event
async def on_message(message:discord.Message):
    guild = message.guild
    if not guild: return
    gid = message.guild.id
    voice = message.author.voice

    # 読み上げ
    # 発言者がチャンネルに入っているか
    if not message.author.voice:
        return

    # 発言者がBotの場合はPass
    if message.author.bot:
        return
    
    # 今世紀最大検知
    if not '今世紀最大' in message.content:
        return

    print(f'\n#今世紀最大 検知！  : {guild.name} ({message.channel.name})')
    print( message.author.name +" (",message.author.display_name,') : '+ message.content)

    if voice.channel and not guild.voice_client:
        await join(message)

    try: await g_opts[gid].play_konseiki()
    except KeyError:pass

    # Fin
    await client.process_commands(message)



class DataInfo:
    def __init__(self, guild:discord.Guild):
        self.guild = guild
        self.gn = guild.name
        self.gid = guild.id
        self.vc = guild.voice_client
        self.MA = MultiAudio(guild, client, self)
        self.loop = client.loop
        self.client = client


    async def play_konseiki(self):
        Vvc = self.MA.add_player(opus=False)
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