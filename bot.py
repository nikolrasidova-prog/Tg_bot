import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ===============================
# ВСТАВЬ СВОЙ БОТ ТОКЕН и ADMIN_ID В ЭТИ ПЕРЕМЕННЫЕ
# ===============================
# НЕ вставляй токен прямо в код, лучше на Render:
# BOT_TOKEN = 8248333706:AAEwKH69lYXXmqXuF_PuaPO-rwbBhaei510
# ADMIN_ID = 6563977013
# ===============================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # сюда на Render ставишь BOT_TOKEN
PARTNER_LINK = os.getenv("PARTNER_LINK", "https://partner-link.com")
ADMIN_ID = os.getenv("ADMIN_ID")     # сюда ставишь свой Telegram ID на Render

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

profiles = [
    {"name": "Анна", "age": 28, "text": "Ищу общение и новые знакомства 😊"},
    {"name": "Елена", "age": 29, "text": "Люблю активный отдых, жду общения!"},
    {"name": "Марина", "age": 30, "text": "Ищу серьёзного человека ❤️"},
    {"name": "Ольга", "age": 31, "text": "Люблю путешествовать, приглашаю познакомиться!"},
    {"name": "Татьяна", "age": 32, "text": "Весёлая и открытая, пишите!"},
    {"name": "Наталья", "age": 33, "text": "Готова к новым знакомствам!"},
    {"name": "Ирина", "age": 34, "text": "Люблю кофе и вечерние прогулки ☕"},
    {"name": "Светлана", "age": 35, "text": "Ищу интересного собеседника 😊"},
    {"name": "Виктория", "age": 36, "text": "Жду новых впечатлений и знакомств!"},
    {"name": "Анастасия", "age": 37, "text": "Люблю кино и прогулки на природе"},
    {"name": "Юлия", "age": 38, "text": "Пишу сама, буду рада общению!"},
    {"name": "Ксения", "age": 39, "text": "Весёлая и активная, ищу друзей и общение"},
    {"name": "Оксана", "age": 40, "text": "Хочу познакомиться с интересными людьми!"},
    {"name": "Екатерина", "age": 42, "text": "Люблю путешествия и новые знакомства"},
    {"name": "Дарья", "age": 45, "text": "Открыта к общению и новым друзьям"},
]

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    users = load_users()
    if message.from_user.id not in users:
        users.append(message.from_user.id)
        save_users(users)

    text = "Привет! Я бот знакомств.\nВыбирай анкету ниже и пиши женщине через кнопку.\n"
    keyboard = types.InlineKeyboardMarkup()
    for profile in profiles:
        btn = types.InlineKeyboardButton(
            text=f"{profile['name']}, {profile['age']}",
            url=PARTNER_LINK
        )
        keyboard.add(btn)
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(commands=["broadcast"])
async def cmd_broadcast(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        await message.reply("У тебя нет прав для рассылки.")
        return

    users = load_users()
    args = message.get_args()
    if not args:
        await message.reply("Напиши текст после команды: /broadcast Текст рассылки")
        return

    for user_id in users:
        try:
            await bot.send_message(user_id, args)
        except:
            pass
    await message.reply(f"Рассылка отправлена {len(users)} пользователям.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
