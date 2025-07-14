from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

# Token va kanal
TOKEN = "7876511816:AAGuZ6kzRqhI3gdYqwRoGINxGvVyvZ7326w"
REQUIRED_CHANNEL = "@Mr_Yahyobe"

# Kanalga a'zo bo'lganini tekshiruvchi funksiya
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Instagram video yuklab beruvchi botga xush kelibsiz!\nFoydalanish uchun Instagram ssilkani yuboring.")

# Instagram link kelganda
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if not await is_subscribed(user_id, context):
        await update.message.reply_text(f"📛 Avval {REQUIRED_CHANNEL} kanaliga obuna bo‘ling!\nObuna bo‘lgach qayta urinib ko‘ring.")
        return

    if "instagram.com" not in text:
        await update.message.reply_text("📎 Iltimos, faqat Instagram videosining to‘liq ssilkasini yuboring.")
        return

    msg = await update.message.reply_text("🔍 Yuklanmoqda...")

    try:
        ydl_opts = {
            'outtmpl': 'insta.%(ext)s',
            'format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            file_name = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file_name, 'rb'), caption="✅ Yuklab olindi!")
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik yuz berdi: {e}")

    await msg.delete()

# Botni ishga tushurish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
