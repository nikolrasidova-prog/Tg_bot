import logging
import os
import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN", "8248333706:AAEwKH69lYXXmqXuF_PuaPO-rwbBhaei510")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

PARTNER_LINK = "https://partner-link.com"
USERS_FILE = "users.json"
ADMIN_ID = 6563977013  # <--- ВСТАВЬ СВОЙ TELEGRAM ID

waiting_for_broadcast = {}
pending_message = {}

profiles = [
    {"name": "Анна", "age": 32, "photo": "https://i.imgur.com/1.jpg", "text": "Привет, я Анна! Люблю готовить ❤️"},
    {"name": "Марина", "age": 45, "photo": "https://i.imgur.com/2.jpg", "text": "Я Марина. Ищу заботливого мужчину 🥂"},
    {"name": "Елена", "age": 39, "photo": "https://i.imgur.com/3.jpg", "text": "Я обожаю путешествовать и танцевать 💃"},
    {"name": "Ольга", "age": 41, "photo": "https://i.imgur.com/4.jpg", "text": "Я Ольга, ищу серьёзные отношения ❤️"},
    {"name": "Ирина", "age": 28, "photo": "https://i.imgur.com/5.jpg", "text": "Люблю активный отдых и спорт 🏞️"},
    {"name": "Светлана", "age": 49, "photo": "https://i.imgur.com/6.jpg", "text": "Готова к новым знакомствам и эмоциям 💌"},
    {"name": "Ксения", "age": 36, "photo": "https://i.imgur.com/7.jpg", "text": "Люблю уютные вечера и вкусный кофе ☕"},
    {"name": "Татьяна", "age": 43, "photo": "https://i.imgur.com/8.jpg", "text": "Жду мужчину, который ценит искренность 🌹"}
]

# --- Работа с пользователями ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

def remove_user(user_id):
    users = load_users()
    if user_id in users:
        users.remove(user_id)
        save_users(users)

def get_profile():
    return random.choice(profiles)

def profile_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❤️ Познакомиться", url=PARTNER_LINK))
    kb.add(InlineKeyboardButton("➡ Следующая", callback_data="next_profile"))
    return kb

# --- Команды ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    add_user(message.from_user.id)
    profile = get_profile()
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=profile["photo"],
        caption=f"{profile['name']}, {profile['age']} лет\n\n{profile['text']}",
        reply_markup=profile_keyboard()
    )

@dp.message_handler(commands=['stop'])
async def stop_cmd(message: types.Message):
    remove_user(message.from_user.id)
    await message.answer("Вы отписались от рассылки 💔")

@dp.message_handler(commands=['send'])
async def send_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас нет прав для этой команды.")
    waiting_for_broadcast[message.from_user.id] = True
    await message.answer("✍ Напиши текст рассылки или прикрепи фото — я покажу предпросмотр перед отправкой.")

@dp.message_handler(content_types=["text", "photo"])
async def handle_message(message: types.Message):
    global waiting_for_broadcast, pending_message
    if waiting_for_broadcast.get(message.from_user.id):
        pending_message[message.from_user.id] = message
        waiting_for_broadcast[message.from_user.id] = False

        # Показываем предпросмотр
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Отправить", callback_data="confirm_send"))
        kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_send"))

        if message.photo:
            await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption or "—", reply_markup=kb)
        else:
            await message.answer(f"📢 Предпросмотр:\n\n{message.text}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ["confirm_send", "cancel_send"])
async def handle_send_decision(callback: types.CallbackQuery):
    global pending_message
    msg = pending_message.get(callback.from_user.id)
    if not msg:
        return await callback.answer("Нет сообщения для рассылки.", show_alert=True)

    if callback.data == "cancel_send":
        pending_message.pop(callback.from_user.id)
        return await callback.message.edit_text("❌ Рассылка отменена.")

    # Отправка всем пользователям
    users = load_users()
    sent = 0
    for user_id in users:
        try:
            if msg.photo:
                await bot.send_photo(user_id, msg.photo[-1].file_id, caption=msg.caption or "")
            else:
                await bot.send_message(user_id, msg.text)
            sent += 1
        except Exception as e:
            print(f"Ошибка {user_id}: {e}")

    pending_message.pop(callback.from_user.id)
    await callback.message.edit_text(f"✅ Рассылка завершена. Отправлено {sent} пользователям.")

@dp.callback_query_handler(lambda c: c.data == "next_profile")
async def next_profile(callback: types.CallbackQuery):
    profile = get_profile()
    await callback.message.delete()
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=profile["photo"],
        caption=f"{profile['name']}, {profile['age']} лет\n\n{profile['text']}",
        reply_markup=profile_keyboard()
    )

# --- Web-сервер для Railway ---
async def handle(request):
    return web.Response(text="Bot is running!")

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get("/", handle)
    from threading import Thread

    def start_polling():
        executor.start_polling(dp, skip_updates=True)

    Thread(target=start_polling).start()
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

