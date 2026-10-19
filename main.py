import requests, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8883517107:AAGujPD23ChKWUSfKkSy1cd_FraRI2Qv15Q"
TMDB_API_KEY = "84ed29fda7f14922a4542f523a1fb267"
CHANNEL = "@Muvflix"

def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    try:
        return requests.get(url, timeout=10).json().get("results", [])
    except:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎬 *Welcome to Muvflix Bot!*\n\n"
        "Your ultimate movie companion.\n\n"
        "Just send me any movie name and I'll find it.\n"
        "Example: `John Wick` or `Avatar`\n\n"
        f"Join us: {CHANNEL}"
    )
    buttons = [
        [InlineKeyboardButton("🔥 Trending Today", callback_data="trending")],
        [InlineKeyboardButton("🎲 Random Movie", callback_data="random")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ *How to use:*\n1. Type movie name\n2. /search <name>\n3. /trending\n4. /random", parse_mode="Markdown")

async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("🔍 Example: `/search John Wick`", parse_mode="Markdown")
        return
    await do_search(update, query)

async def trending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
    data = requests.get(url, timeout=10).json()
    movies = data.get("results", [])[:5]
    text = "🔥 *Today's Trending:*\n\n" + "\n".join([f"{i+1}. {m['title']} ({m.get('release_date','')[:4]}) - ⭐ {m['vote_average']}" for i,m in enumerate(movies)])
    await update.message.reply_text(text, parse_mode="Markdown")

async def random_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    movies = requests.get(url, timeout=10).json().get("results", [])
    if movies:
        await send_movie_card(update, random.choice(movies))

async def do_search(update, query):
    results = search_movie(query)
    if not results:
        await update.message.reply_text(f"😔 No movie found for '{query}'")
        return
    await send_movie_card(update, results[0])

async def send_movie_card(update, movie):
    title = movie['title']
    rating = movie['vote_average']
    date = movie.get('release_date','N/A')
    overview = movie.get('overview','No overview')[:400]
    poster_path = movie.get('poster_path')
    text = f"🎬 *{title}* ({date[:4]})\n⭐ {rating}/10\n\n{overview}...\n\n"
    btn = InlineKeyboardButton("🎥 Watch Trailer", url=f"https://www.youtube.com/results?search_query={title}+trailer")
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        await update.message.reply_photo(photo=poster_url, caption=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[btn]]))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[btn]]))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await do_search(update, update.message.text)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("search", search_cmd))
app.add_handler(CommandHandler("trending", trending_cmd))
app.add_handler(CommandHandler("random", random_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("Muvflix Bot is running...")
app.run_polling()
