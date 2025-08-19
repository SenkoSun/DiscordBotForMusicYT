from vkpymusic import Service
from config import VK_TOKEN
from config import VK_USER_ID

USER_CLIENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

service = Service(USER_CLIENT, VK_TOKEN)


audios = service.get_songs_by_userid(VK_USER_ID, 10)  # Если None — текущий пользователь
for audio in audios:
    print(f"{audio.artist} - {audio.title} | URL: {audio.url}")