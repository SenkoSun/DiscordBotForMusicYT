import yt_dlp
import asyncio

async def get_audio_stream_url(youtube_url):
    ydl_opts = {
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
        'source_address': '0.0.0.0'
    }
    
    # Запускаем синхронный код в отдельном потоке
    def sync_extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(youtube_url, download=False)
    
    try:
        # Используем asyncio для выполнения синхронного кода асинхронно
        info = await asyncio.to_thread(sync_extract)
        return info['url']  # Ссылка на аудиопоток
    except Exception as e:
        print(f"Ошибка при получении аудио: {e}")
        return None