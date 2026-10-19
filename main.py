import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8300000000:AAH_YOUR_REAL_TOKEN_HERE"
TMDB_API_KEY = "YOUR_TMDB_KEY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Muvflix! Send me a movie name.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={q}"
    r = requests.get(url).json()
    if r.get('results'):
        m = r['results'][0]
        await update.message.reply_text(f"🎬 {m['title']}\n\n{m.get('overview','')}")
    else:
        await update.message.reply_text("Movie not found")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
print("Muvflix Bot is running...")
app.run_polling()
