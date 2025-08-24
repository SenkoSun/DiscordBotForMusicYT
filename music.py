import yt_dlp
import asyncio
import random


def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    return random.choice(user_agents)


async def get_audio_stream_url(youtube_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                'restrictfilenames': True,
                'noplaylist': False,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'logtostderr': False,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'auto',
                'source_address': '0.0.0.0',
                'http_headers': {
                    'User-Agent': get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['configs'],
                    }
                },
            }
            
            def sync_extract():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(youtube_url, download=False)
            
            info = await asyncio.to_thread(sync_extract)
            if info and '_type' in info and info['_type'] == 'playlist':
                # Плейлист - возвращаем все entries
                return [entry for entry in info.get('entries', []) if entry] \
                +  [{
                    'title': info.get('title', 'Без названия'),
                    'webpage_url': info.get('webpage_url', ''),
                    'uploader': info.get('uploader', 'Неизвестный автор'),
                    'thumbnail': info.get('thumbnail', ''),
                    'playlist_count': len(info.get('entries', []))
                    }]
            else:
                return [info] 
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Ошибка после {max_retries} попыток: {e}")
                return None
            await asyncio.sleep(2)