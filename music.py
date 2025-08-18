import aiovk
from config import VK_TOKEN

async def search_vk_music(query):
    session = aiovk.TokenSession(access_token=VK_TOKEN)
    vk_api = aiovk.API(session)
    result = await vk_api.audio.search(q=query, count=1)  # Получаем первый трек
    if not result["items"]:
        return None
    track = result["items"][0]
    return {
        "title": f"{track['artist']} - {track['title']}",
        "url": track["url"]
    }