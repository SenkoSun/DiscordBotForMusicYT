from config import BOT_TOKEN
import discord
from discord.ext import commands
from music import search_vk_music

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

@bot.command()
async def play(ctx, *, query):
    # Проверяем, что автор в голосовом канале
    if not ctx.author.voice:
        await ctx.send("Зайдите в голосовой канал!")
        return

    # Ищем трек в VK
    track = await search_vk_music(query)
    if not track:
        await ctx.send("Трек не найден 😢")
        return

    # Подключаемся к голосовому каналу
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        voice_client = await voice_channel.connect()
    else:
        voice_client = ctx.voice_client

    # Воспроизводим трек через FFmpeg
    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(track["url"]))

    await ctx.send(f"🎶 Сейчас играет: **{track['title']}**")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Воспроизведение остановлено.")
    else:
        await ctx.send("Бот не в голосовом канале!")


bot.run(BOT_TOKEN)
if __name__ == '__main__':
    bot.run(BOT_TOKEN)