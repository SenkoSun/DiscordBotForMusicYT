from config import BOT_TOKEN
import discord
import asyncio
from discord.ext import commands
from music import get_audio_stream_url

intents = discord.Intents.default() # Подключаем "Разрешения"
intents.message_content = True
intents.voice_states = True
# Задаём префикс и интенты
bot = commands.Bot(command_prefix='/', intents=intents) 

async def leave(ctx):
    # Отключаем бота от голосового канала
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Отключился от голосового канала")
    else:
        await ctx.send("Я не в голосовом канале!")

@bot.command(name='play')
async def play(ctx, url: str):
    """Воспроизводит аудио из прямого URL-потока"""
    
    # Проверка подключения пользователя
    if not ctx.author.voice:
        return await ctx.send("Вы не в голосовом канале!")
    
    voice_client = ctx.voice_client
    
    # Подключение к каналу
    if not voice_client:
        voice_client = await ctx.author.voice.channel.connect()
    elif voice_client.channel != ctx.author.voice.channel:
        await voice_client.move_to(ctx.author.voice.channel)
    
    async with ctx.typing():
        try:
            # Создаем аудио источник из URL
            
            audio_source = discord.FFmpegPCMAudio(await get_audio_stream_url(url))
            
            # Проверяем, что источник валидный
            if not audio_source.is_opus():
                # Добавляем преобразование, если нужно
                audio_source = discord.PCMVolumeTransformer(audio_source)
            
            # Воспроизводим
            voice_client.play(audio_source, after=lambda e: print(f'Ошибка: {e}') if e else None)
            audio_source = discord.FFmpegPCMAudio(url)

            await ctx.send(f"🎶 Воспроизводится аудио поток")
            
        except Exception as e:
            await ctx.send(f"Ошибка: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Воспроизведение остановлено.")
    else:
        await ctx.send("Бот не в голосовом канале!")

@bot.command()
async def start(ctx):
    await ctx.send("Привет!\n" \
                   "Я бот для музыки из ВК!")


if __name__ == '__main__':
    bot.run(BOT_TOKEN)