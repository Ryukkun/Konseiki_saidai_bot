import asyncio
from discord import FFmpegOpusAudio, FFmpegPCMAudio



class StreamAudioData:

    def __init__(self,url):
        self.Url = url
        self.loop = asyncio.get_event_loop()
        self.Web_Url = None
        self.St_Vol = None
        self.St_Sec = None
        self.St_Url = None
        self.music = None
        self.YT = None
        self.CH_Icon = None
        


    def Url_Only(self):
        self.St_Url = self.Url
        self.music = False
        self.YT = False
        return self


    async def AudioSource(self, opus:bool):
        FFMPEG_OPTIONS = {'options': '-vn -application lowdelay -loglevel quiet'}
        if self.music:
            volume = -20.0
            if Vol := self.St_Vol:
                Vol /= 2
                volume -= Vol
            FFMPEG_OPTIONS['before_options'] = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -analyzeduration 2147483647 -probesize 2147483647"
            FFMPEG_OPTIONS['options'] += f' -af "volume={volume}dB"'

        if opus:
            FFMPEG_OPTIONS['options'] += ' -c:a libopus'
            return await FFmpegOpusAudio.from_probe(self.St_Url,**FFMPEG_OPTIONS)

        else:
            FFMPEG_OPTIONS['options'] += ' -c:a pcm_s16le -b:a 128k'
            return FFmpegPCMAudio(self.St_Url,**FFMPEG_OPTIONS)
