import os
import discord
import youtube_dl

from random import choice

from discord.ext import commands, tasks
from discord.utils import get
from discord import FFmpegPCMAudio

from youtube_dl import YoutubeDL

from dotenv import load_dotenv

youtube_dl.utils.bug_reports_message = lambda: ''

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

config = {
    'token': BOT_TOKEN,
    'prefix': '!',
}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


client = commands.Bot(
    command_prefix=config['prefix'], intents=discord.Intents.all())

status = ['Х', 'У', 'Й', "Детка ты на это падкая"]
queue = []
roles = ['Еврей и горжусь этим', "Татары"]


@client.event
async def on_ready():
    # send_dima_lox.start()
    print('Bot is online!')
    print('Если возникает ошибка ffmpeg not found - проверь папку с ffmpeg-ом в path если там траблы папку с кодеком \n'
          'перемести на диск С и добавь в path-е')


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `?help` command for details!')


@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Задержка: {round(client.latency * 1000)}ms')


@client.command(name='q', help='Эта команда добавляет трек в очередь')
async def q(ctx, url):
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` добавлено в очередь!')


@client.command(name='remove', help='Эта команда удаляет трек из очереди')
async def remove(ctx, number):
    global queue

    try:
        del (queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')

    except:
        await ctx.send('Ваша очередь и так пуста!')


@client.command(name='play', help='Команда для воспроизведения музыки')
async def play(ctx, url=None):
    global queue
    if url is None and len(queue) == 0:
        await ctx.send("Ваша очередь пуста")
        return
    if not ctx.message.author.voice:
        await ctx.send("Вы не находитесь в голосовом канале")
        return
    elif ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()

    if url is None:
        url = queue[0]

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Bot is playing')


# check if the bot is already playing
    else:
        await ctx.send("Бот уже играет")
        return
    del (queue[0])


@client.command(name='pause', help='Эта команда приостанавливает воспроизведение')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()


@client.command(name='resume', help='Эта команда возобновляет воспроизведение')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()


@client.command(name='view', help='Эта команда показывает очередь')
async def view(ctx):
    if queue == []:
        await ctx.send(f'Че пялишь? Пусто епты!')
    else:
        await ctx.send(f'Your queue is now `{queue}!`')


@client.command(name='stop', help='Эта команда осуществляет остановку воспроизведения')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.stop()
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@commands.has_permissions(administrator=True)
@client.command(name="kick", help='Эта команда кикает участника')
async def kick(ctx, member: discord.Member, *, reason="Ну нахуй с пляжа получается"):
    await member.kick(reason=reason + " Нахуй с пляжа")


@commands.has_permissions(administrator=True)
@client.command(name='ban', help='Эта команда банит участника')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Пользователь забанен по причине: {reason}')


@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.name}#{user.dicriminator}')


@tasks.loop(hours=2)
async def send_dima_lox():
    main_channel = client.get_channel(898886246808559678)
    user = get(client.users, name="FILLADEK", discriminator="4864")
    await main_channel.send(f'{user.mention} Дима лох')


client.run(token=config['token'])
