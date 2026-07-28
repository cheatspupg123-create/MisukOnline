import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import requests
from bs4 import BeautifulSoup

# Твой токен бота
TOKEN = "8600446397:AAEGqFV_3DCj10rIhWYt0fWkbGp-Bm75y34"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 🎵 Отправь мне название песни или исполнителя, "
        "и я попробую найти для тебя аудиофайл в интернете."
    )

@dp.message(F.text)
async def search_song(message: types.Message):
    query = message.text
    waiting_msg = await message.answer(f"🔎 Ищу трек: *{query}*...", parse_mode="Markdown")
    
    try:
        search_url = f"https://yandex.ru/search/?text={query.replace(' ', '+')}+mp3"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            mp3_link = None
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '.mp3' in href.lower() and href.startswith('http'):
                    mp3_link = href
                    break
            
            await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
            
            if mp3_link:
                try:
                    await message.answer_audio(audio=mp3_link, caption=f"🎵 Вот что удалось найти по запросу: {query}")
                except Exception:
                    await message.answer(f"Нашел ссылку на трек, но Telegram не смог её подгрузить напрямую:\n{mp3_link}")
            else:
                await message.answer("😔 К сожалению, прямой mp3-файл по этому запросу не нашлось. Попробуй уточнить название или имя исполнителя.")
        else:
            await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
            await message.answer("⚠️ Ошибка при обращении к поискочнику. Попробуй позже.")
            
    except Exception as e:
        logging.error(f"Ошибка поиска: {e}")
        await bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)
        await message.answer("❌ Произошла ошибка при поиске. Попробуй еще раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
