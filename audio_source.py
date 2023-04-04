import asyncio
from discord import FFmpegOpusAudio, FFmpegPCMAudio



class StreamAudioData:

    def __init__(self,url):
        self.url = url
        self.loop = asyncio.get_event_loop()
        self.web_url = None
        self.st_vol = None
        self.st_sec = None
        self.st_url = None
        self.ch_icon = None
        


    def Url_Only(self):
        self.st_url = self.url
        return self


    async def AudioSource(self, opus:bool, **kwargs):
        FFMPEG_OPTIONS = {'options': '-vn -application lowdelay -loglevel quiet'}

        if opus:
            FFMPEG_OPTIONS['options'] += ' -c:a libopus'
            return await FFmpegOpusAudio.from_probe(self.st_url,**FFMPEG_OPTIONS)

        else:
            FFMPEG_OPTIONS['options'] += ' -c:a pcm_s16le -b:a 128k'
            return FFmpegPCMAudio(self.st_url,**FFMPEG_OPTIONS)
