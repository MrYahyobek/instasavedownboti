
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramBadRequest

# TOKEN
API_TOKEN = "7876511816:AAE0n2TTn7qXvxLyq3OfU1Hvr5BviHFcCFw"

# Kanal username
CHANNEL_USERNAME = "@Mr_Yahyobe"

# Admin ID (o'zingizning Telegram ID ni yozasiz!)
ADMIN_ID =  6378794790

# Foydalanuvchilar ma'lumotlari
users = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def check_subscription(user_id: int) -> bool:
    """
    Kanalga obuna bo'lgan-bo'lmaganini tekshiradi
    """
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False


@dp.message(CommandStart())
async def start_handler(msg: Message):
    ref_id = None
    if msg.text and len(msg.text.split()) > 1:
        ref_id = msg.text.split()[1]

    user_id = msg.from_user.id
    if user_id not in users:
        users[user_id] = {"referrals": 0, "invited": set(), "awaiting_ad": False}

    if ref_id and ref_id.isdigit():
        ref_id = int(ref_id)
        if ref_id != user_id and user_id not in users[ref_id]["invited"]:
            users[ref_id]["referrals"] += 1
            users[ref_id]["invited"].add(user_id)

    await msg.answer(
        f"Salom, {msg.from_user.first_name}! 👋\n"
        f"Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga obuna bo‘ling va 4ta do‘stni taklif qiling.\n\n"
        f"Referal linkingiz: https://t.me/{(await bot.get_me()).username}?start={user_id}"
    )


# === ADMIN PANEL ===
@dp.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        await msg.answer("❌ Siz admin emassiz!")
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="📢 Reklama yuborish")],
        ],
        resize_keyboard=True
    )
    await msg.answer("🔐 Admin panelga xush kelibsiz!", reply_markup=kb)


@dp.message(lambda m: m.text == "📊 Statistika")
async def stats_handler(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    total_users = len(users)
    await msg.answer(f"📊 Bot foydalanuvchilari soni: {total_users} ta")


@dp.message(lambda m: m.text == "📢 Reklama yuborish")
async def reklama_handler(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    users[msg.from_user.id]["awaiting_ad"] = True
    await msg.answer("✍️ Reklama matnini yuboring:")


@dp.message()
async def handle_message(msg: Message):
    user_id = msg.from_user.id

    # Agar admin reklama matnini yuborayotgan bo'lsa
    if user_id == ADMIN_ID and users.get(user_id, {}).get("awaiting_ad"):
        text = msg.text
        users[user_id]["awaiting_ad"] = False

        count = 0
        for uid in users.keys():
            try:
                await bot.send_message(uid, f"📢 Reklama:\n\n{text}")
                count += 1
            except:
                pass
        await msg.answer(f"✅ Reklama {count} foydalanuvchiga yuborildi")
        return

    # Oddiy foydalanuvchi xabari
    if not await check_subscription(user_id):
        await msg.answer(f"❌ Botdan foydalanish uchun avval {CHANNEL_USERNAME} kanaliga obuna bo‘ling.")
        return

    referrals = users.get(user_id, {}).get("referrals", 0)
    if referrals < 4:
        await msg.answer(f"❌ Sizning hozirgi referallaringiz: {referrals}/4.\n"
                         "Botdan foydalanish uchun 4ta do‘stni taklif qilishingiz kerak.")
        return

    # === Instagram yuklash joyi ===
    await msg.answer("✅ Siz barcha shartlarni bajardingiz.\n\n📥 Instagram video yuklash funksiyasi shu yerda bo‘ladi.\n"
                     "Hozircha bu qism API ulanmagan. (RapidAPI yoki boshqa API ulash kerak)")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
