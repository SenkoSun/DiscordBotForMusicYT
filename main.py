from config import BOT_TOKEN
import discord
import asyncio
from discord import Embed, Colour
from discord import app_commands
from discord.ext import commands
from music import get_audio_stream_url

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='/', intents=intents) 


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
        return await interaction.followup.send("Вы не в голосовом канале!", delete_after=5.0, ephemeral=True)
    
    voice_client = interaction.guild.voice_client
    

    if not voice_client:
        voice_client = await interaction.user.voice.channel.connect()
    elif voice_client.channel != interaction.user.voice.channel:
        await voice_client.move_to(interaction.user.voice.channel)
        
    await interaction.response.defer(thinking=True)
    try:
        info = await get_audio_stream_url(url)
        audio_source = discord.FFmpegPCMAudio(
            info['url'],
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -b:a 256k -bufsize 512k'
        )
        
        if not audio_source.is_opus():
            audio_source = discord.PCMVolumeTransformer(audio_source)
        
        voice_client.play(audio_source, after=lambda e: print(f'Ошибка: {e}') if e else None)

        embed = discord.Embed(
            color = 0xFF0000,
            title = info['title'],
            description= info['channel'],
            url = url
        )
        embed.set_author(name="Трек добавлен!")

        embed.add_field(name="Длительность", value = f"{info['duration_string']}", inline=False)

        embed.set_thumbnail(url = info['thumbnails'][-1]['url'])

        await interaction.followup.send(embed=embed)
            
    except Exception as e:
        await interaction.followup.send(f"Ошибка: {str(e)}", ephemeral=True)


@bot.tree.command(name="stop", description="Остановка воспроизведения и очистка очереди")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        voice_client.stop()
        await voice_client.disconnect()
        await interaction.response.send_message("⏹️ Воспроизведение остановлено.", delete_after=5.0)
    else:
        await interaction.response.send_message("Бот не в голосовом канале!", delete_after=5.0, ephemeral=True)

    
@bot.tree.command(name="pause", description="Пауза/снятие с паузы")
async def start(interaction: discord.Interaction):
    
    if not interaction.user.voice:
        return await interaction.response.send_message("Вы не в голосовом канале!", delete_after=5.0, ephemeral=True)
    
    voice_client = interaction.guild.voice_client

    if voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Пауза снята", delete_after=5.0)
        return

    if not voice_client.is_playing():
        await interaction.response.send_message("Сейчас ничего не играет!", delete_after=5.0, ephemeral=True)
        return

    voice_client.pause()
    await interaction.response.send_message("⏸️ Пауза поставлена", delete_after=5.0)
    

    if not voice_client:
        voice_client = await interaction.user.voice.channel.connect()
    elif voice_client.channel != interaction.user.voice.channel:
        await voice_client.move_to(interaction.user.voice.channel)
    
@bot.tree.command(name="info", description="Техническая информация о боте")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message("Привет!\n" \
                   "Я бот для музыки из ВК!")
    

if __name__ == '__main__':
    bot.run(BOT_TOKEN)