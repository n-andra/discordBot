# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 20:30:11 2020

@author: NABIL
"""

import discord
import nest_asyncio
import youtube_dl
nest_asyncio.apply()
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)    

client = commands.Bot(command_prefix = '.')
jazzUrl = 'https://www.youtube.com/watch?v=M4sEcIHG0Yc'

#Above is all the setup for utilisng YTDL (Which is appearantly necessary)
#As well as ffmpeg. 
#Nest Asyncio is used due to something along the lines of coroutine being unavailable in
#python, and lastly discord and discort.ext commands so that we can create bot commands
#client represents the bot's status + what is needed to call the bot's commands
#url is the link to FREE FORM JAZZ.

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get(jazzUrl)

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop 
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(jazzUrl, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


#YTDLSource is to be used within the commands.

@client.event 
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Acquiring a taste for..."))
    print("Bot is ready.")
    
@client.event
async def on_disconnect():
    print("Bot has disconnected.")
    
@client.command()
async def ping(ctx):
    await ctx.send('Pong!')
    
@client.command()
async def jazz(ctx):
   connection = ctx.author.voice
   print(connection)
   if connection:
        connectToChannel = connection.channel.connect()
        await connectToChannel
        print("Bot is connected to" +str(connection))
        server = ctx.message.guild
        print(server)
        audioSource = await discord.FFmpegOpusAudio.from_probe(jazzUrl)
        server.voice_client.play(audioSource)
        print("Bot is now playing free form jazz")
        await client.close()
        print("Bot has now closed/turned off")
    
@client.command()
async def jazz2(ctx):    
    authorVoiceState = ctx.author.voice
    if authorVoiceState:
        voice_client = await authorVoiceState.channel.connect()
        print("Bot is connected to " +str(authorVoiceState.channel.name))
        player = await YTDLSource.from_url(jazzUrl, stream=True)
        voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.channel.send('Now playing: {}'.format(player.title))
        
@client.command()
async def deleteMsgs(ctx):
    await ctx.channel.purge(limit=10)    
    print('Messages deleted!')
    
client.run('key here')
