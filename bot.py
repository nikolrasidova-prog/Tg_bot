import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- Настройки логов ---
logging.basicConfig(level=logging.INFO)

# --- Конфигурация ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8248333706:AAEwKH69lYXXmqXuF_PuaPO-rwbBhaei510")
ADMIN_ID = os.getenv("ADMIN_ID", "6563977013")
PARTNER_LINK = os.getenv("PARTNER_LINK", "https://partner-link.com")

# --- Проверка наличия токена ---
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN. Добавь его в Render → Environment Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Анкеты ---
profiles = [
    {"name": "Ольга, 34", "bio": "Серьезные отношения. Ищу заботливого мужчину ❤️"},
    {"name": "Марина, 41", "bio": "Хочу познакомиться, люблю готовить и уют 🏡"},
    {"name": "Татьяна, 29", "bio": "Люблю путешествия ✈️ и романтику 🌹"},
    {"name": "Анна, 37", "bio": "Детей нет, хочу любви 💕"},
    {"name": "Ирина, 45", "bio": "Скучно одной... Пиши! 😉"},
    {"name": "Наталья, 32", "bio": "Занимаюсь спортом, ищу активного мужчину 🏃‍♂️"},
    {"name": "Елена, 39", "bio": "Серьезная, семейные ценности важны ❤️"},
    {"name": "Алёна, 28", "bio": "Яркая, веселая, люблю сюрпризы 🎁"},
    {"name": "Светлана, 49", "bio": "Хочу найти верного спутника жизни 💍"},
    {"name": "Вера, 33", "bio": "Люблю животных 🐶 и уютные вечера ☕"},
]

# --- Команда /start ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("👋 Привет! Смотри анкеты и знакомься!")
    for p in profiles:
        text = f"👩 {p['name']}\n{p['bio']}\n➡️ [Смотреть анкету]({PARTNER_LINK})"
        await message.answer(text, parse_mode="Markdown")

# --- Команда /broadcast (только для админа) ---
@dp.message_handler(commands=['broadcast'])
async def broadcast(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        return await message.reply("⛔ У тебя нет прав для рассылки.")
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        return await message.reply("❗ Напиши текст после команды.")
    # Тут можно сделать рассылку пользователям (нужна база)
    await message.reply(f"📢 Сообщение для рассылки: {text}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
