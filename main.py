from config import BOT_TOKEN
import discord
import asyncio
from discord import Embed, Colour
from discord import app_commands
from discord.ext import commands
from music import get_audio_stream_url
from collections import deque
import random

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='/', intents=intents)

servers = dict()

def get_queue(guild_id) -> deque:
    if guild_id not in servers:
        servers[guild_id] = deque()
    return servers[guild_id]


class Track():
     def __init__(self, info):
        self.url = info['webpage_url']
        self.audio = info['url']
        self.title = info['title']
        self.channel = info['channel']
        self.time = info['duration_string']
        self.image = info['thumbnails'][-1]['url']



@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")


@bot.tree.command(name="play", description="Добавляет в очередь трек")
@app_commands.describe(url="Ссылка на видео")
async def play(interaction: discord.Interaction, url: str):
    """Воспроизводит аудио из прямого URL-потока"""

    
    if not interaction.user.voice:
        await interaction.response.send_message("Вы не в голосовом канале!", delete_after=5.0)
        return
    
    voice_client = interaction.guild.voice_client
    
    if not voice_client: 
        voice_client = await interaction.user.voice.channel.connect()
    elif voice_client.channel != interaction.user.voice.channel:
        await voice_client.move_to(interaction.user.voice.channel)
    
        
    try:
        await interaction.response.defer(thinking=True)

        info = await get_audio_stream_url(url)
        queue = get_queue(interaction.guild.id)

        if (len(info) == 0):
            info = info[0]
            queue.appendleft(Track(info))

            track = Track(info)
            embed = discord.Embed(
                color = 0xFF0000,
                title = track.title,
                description= track.channel,
                url = track.url
            )
            
            embed.set_author(name="Трек добавлен!")
            embed.add_field(name="Длительность", value = track.time , inline=False)
            embed.set_thumbnail(url = track.image)

        else:
            for i in info[:-1]:
                queue.appendleft(Track(i))
            
            track = info[-1]
            embed = discord.Embed(
                color = 0xFF0000,
                title = track['title'],
                description= track['uploader'],
                url = track['webpage_url']
            )
            
            embed.set_author(name="Плэйлист добавлен!")
            embed.add_field(name="Количество трэкоов", value = f"{track['playlist_count']}" , inline=False)
            embed.set_thumbnail(url = track['thumbnail'])

        await interaction.followup.send(embed=embed)

        if not voice_client.is_playing():
            await play_next(interaction)
            
    except Exception as e:
        await interaction.response.send_message(f"Ошибка: {str(e)}", ephemeral=True,  delete_after=5.0)


async def play_next(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    queue = get_queue(interaction.guild.id)

    if len(queue) == 0:
        return
    
    # await interaction.response.defer(thinking=True)
    if not voice_client.is_playing():
        track = queue.pop()
        audio_source = discord.FFmpegPCMAudio(
            track.audio,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -b:a 256k -bufsize 512k'
        )
        if not audio_source.is_opus():
            audio_source = discord.PCMVolumeTransformer(audio_source)

    
        voice_client.play(audio_source, after=lambda x: asyncio.run_coroutine_threadsafe(
                    play_next(interaction), 
                    bot.loop
                ))


@bot.tree.command(name="queue", description="Вывод очереди")
async def queue(interaction: discord.Interaction):
    embed = discord.Embed(
        title = "**Очередь**",
    )
    
    queue = get_queue(interaction.guild.id)
    for i in range(min(len(queue) - 1, 25), -1, -1):
        if i == len(queue) - 1:
            embed.add_field(name="", value = f"**{len(queue) - i}. {queue[i].channel} - {queue[i].title}**" , inline=False)
        else:
            embed.add_field(name="", value = f"{len(queue) - i}. {queue[i].channel} - {queue[i].title}" , inline=False)

    if len(queue) == 0:
        embed.add_field(name="", value = f"Тут ничего нет 🍃" , inline=False)

    await interaction.response.send_message(embed=embed, ephemeral = True)

@bot.tree.command(name="shuffle", description="Перемешивание очереди")
async def shuffle(interaction: discord.Interaction):
    queue = get_queue(interaction.guild.id)
    queue = deque(random.sample(list(queue), len(queue)))
    servers[interaction.guild_id] = queue
    await interaction.response.send_message("🔀 Очередь перемешана!", ephemeral = True, delete_after=5)


@bot.tree.command(name="stop", description="Остановка воспроизведения и очистка очереди")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        voice_client.stop()
        queue = get_queue(interaction.guild.id)
        queue.clear()
        await voice_client.disconnect()
        await interaction.response.send_message("⏹️ Воспроизведение остановлено.", delete_after=5.0)
    else:
        await interaction.response.send_message("Бот не в голосовом канале!", ephemeral=True, delete_after=5.0)

@bot.tree.command(name="skip", description="Пропуск текущего трека")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        voice_client.stop()
        await interaction.response.send_message("⏭️ Трэк пропущен.", delete_after=5.0)
        await play_next(interaction)
    else:
        await interaction.response.send_message("Бот не в голосовом канале!", ephemeral=True, delete_after=5.0)

    
@bot.tree.command(name="pause", description="Пауза/снятие с паузы")
async def pause(interaction: discord.Interaction):
    
    if not interaction.user.voice:
        await interaction.response.send_message("Вы не в голосовом канале!", ephemeral=True, delete_after=5.0)
        return 
    
    voice_client = interaction.guild.voice_client

    if voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Пауза снята", delete_after=5.0)
        return

    if not voice_client.is_playing():
        await interaction.response.send_message("Сейчас ничего не играет!", ephemeral=True, delete_after=5.0)
        return

    voice_client.pause()
    await interaction.response.send_message("⏸️ Пауза поставлена", delete_after=5.0)
    

    if not voice_client:
        voice_client = await interaction.user.voice.channel.connect()
    elif voice_client.channel != interaction.user.voice.channel:
        await voice_client.move_to(interaction.user.voice.channel)


@bot.tree.command(name="leave", description="Выход из голосового чата")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        voice_client.stop()
        await voice_client.disconnect()
        await interaction.response.send_message("👋", delete_after=5.0)
    else:
        await interaction.response.send_message("Бот не в голосовом канале!", ephemeral=True, delete_after=5.0)
                                                
    
@bot.tree.command(name="info", description="Техническая информация о боте")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎵 Музыкальный Бот",
        description="Бот для воспроизведения музыки с YouTube",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎶 Основные команды",
        value="""**/play** - Воспроизвести трек или плейлист
                **/skip** - Пропустить текущий трек  
                **/stop** - Остановить воспроизведение
                **/queue** - Показать очередь
                **/shuffle** - Перемешать очередь""",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Техническая информация",
        value="""• Поддержка YouTube видео и плейлистов
                    • Автопереход между треками
                    • Высокое качество звука
                    • Стабильное соединение""",
        inline=False
    )
    
    embed.set_footer(text="Бот разработан .senkosun.")
    
    await interaction.response.send_message(embed=embed)
    

if __name__ == '__main__':
    bot.run(BOT_TOKEN)