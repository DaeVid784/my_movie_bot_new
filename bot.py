import telebot
import requests
from groq import Groq
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ၁။ API Keys များ ထည့်သွင်းရန်
TELEGRAM_TOKEN = '7884545102:AAHKQ92OxiIJpYKcnFEvL4JmKf7yQtVlsBI' 
TMDB_API_KEY = '0b39d1c3da2b4c80239d38f4a74d033f'
GROQ_API_KEY = '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' # Groq Console မှရသော gsk_... key ကိုထည့်ပါ

# သင့် Website Link
WEBSITE_BASE_URL = "https://vidsrc.to/embed"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# --- Commands များ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎬 **Movie Finder Bot မှ ကြိုဆိုပါတယ်**\n\n"
        "🔍 **ရှာဖွေပုံ -**\n"
        "• ရုပ်ရှင်နာမည် တိုက်ရိုက်ရိုက်ရှာပါ။\n"
        "• ဇာတ်လမ်းအကြောင်းအရာ ပြောပြပြီး ရှာပါ။\n"
        "📌 Menu ကိုသုံးပြီး Category နဲ့ Trending များ ကြည့်နိုင်ပါတယ်။\n"
	"💡 Tip: Brave Browser ဖြင့်ကြည့်လျှင် ကြော်ငြာမတက်ပါ။"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['category'])
def show_categories(message):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("💥 Action", callback_data="cat_28"), 
               InlineKeyboardButton("😂 Comedy", callback_data="cat_35"))
    markup.row(InlineKeyboardButton("👻 Horror", callback_data="cat_27"), 
               InlineKeyboardButton("❤️ Romance", callback_data="cat_10749"))
    markup.row(InlineKeyboardButton("🧚 Animation", callback_data="cat_16"),
               InlineKeyboardButton("🕵️ Sci-Fi", callback_data="cat_878"))
    bot.send_message(message.chat.id, "ကြည့်ရှုလိုသော အမျိုးအစားကို ရွေးချယ်ပါ-", reply_markup=markup)

@bot.message_handler(commands=['trending'])
def show_trending(message):
    status = bot.reply_to(message, "🔥 နာမည်ကြီးနေတဲ့ ရုပ်ရှင်တွေကို ရှာဖွေနေပါတယ်...")
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}"
    res = requests.get(url).json()
    
    if res.get('results'):
        markup = InlineKeyboardMarkup()
        for m in res['results'][:8]:
            title = m.get('title') or m.get('name')
            m_id = m.get('id')
            markup.add(InlineKeyboardButton(f"🔥 {title}", callback_data=f"info_movie_{m_id}"))
        bot.edit_message_text("ယခုတစ်ပတ်အတွင်း လူကြည့်အများဆုံး ရုပ်ရှင်များ -", message.chat.id, status.message_id, reply_markup=markup)
    else:
        bot.edit_message_text("Trending ရှာမတွေ့ပါ။", message.chat.id, status.message_id)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "❓ **အသုံးပြုပုံ အကူအညီ**\n\n"
        "၁။ ရုပ်ရှင်ရှာရန် - နာမည်တိုက်ရိုက်ရိုက်ပို့ပါ။\n"
        "၂။ ဇာတ်လမ်းဖြင့်ရှာရန် - ဇာတ်လမ်းအကြောင်းအရာကို ပြောပြပါ။\n"
        "၃။ အမျိုးအစားအလိုက်ကြည့်ရန် - /category\n"
        "၄။ လူကြိုက်များတာကြည့်ရန် - /trending"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# --- Callbacks (ခလုတ်နှိပ်ခြင်းများ) ---

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.data.startswith("cat_"):
        genre_id = call.data.split("_")[1]
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&include_adult=false&sort_by=popularity.desc"
        res = requests.get(url).json()
        
        if res.get('results'):
            markup = InlineKeyboardMarkup()
            for m in res['results'][:8]:
                title = m['title']
                m_id = m['id']
                markup.add(InlineKeyboardButton(f"🎬 {title}", callback_data=f"info_movie_{m_id}"))
            bot.edit_message_text("ရွေးချယ်ထားသော အမျိုးအစားမှ ကားများ -", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("info_"):
        _, m_type, m_id = call.data.split("_")
        detail = requests.get(f"https://api.themoviedb.org/3/{m_type}/{m_id}?api_key={TMDB_API_KEY}").json()
        
        title = detail.get('title') or detail.get('name')
        overview = detail.get('overview', 'ဇာတ်လမ်းအကျဉ်းမရှိပါ။')
        poster = detail.get('poster_path')
        watch_url = f"{WEBSITE_BASE_URL}/{m_type}/{m_id}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🍿 အခုကြည့်မယ် (Watch Now)", url=watch_url))
        
        caption = f"✅ **{title}**\n\n📝 {overview[:500]}..."
        
        if poster:
            bot.send_photo(call.message.chat.id, f"https://image.tmdb.org/t/p/w500{poster}", caption=caption, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, caption, reply_markup=markup, parse_mode="Markdown")
        
    bot.answer_callback_query(call.id)

# --- Groq AI ဖြင့် ဇာတ်လမ်းမှ နာမည်ရှာခြင်း ---

def get_title_from_groq(text):
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a movie expert. Identify the official English movie or TV title from the description. Return ONLY the title. If unknown, return 'None'. Example: 'လူပုလေး ၇ ယောက်' -> 'Snow White'"},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content.strip()
    except:
        return text

# --- ရှာဖွေရေး Logic ---

@bot.message_handler(func=lambda message: True)
def handle_search(message):
    user_input = message.text
    status = bot.reply_to(message, "🔍 ရှာဖွေနေပါတယ်...")

    # Groq AI ကိုသုံးပြီး Title ရှာမယ်
    search_query = get_title_from_groq(user_input)

    if search_query.lower() == 'none':
        bot.edit_message_text("ရှာမတွေ့ပါ။", message.chat.id, status.message_id)
        return

    # TMDB Search
    tmdb_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={search_query}&include_adult=false"
    data = requests.get(tmdb_url).json()

    if data.get('results'):
        items = [i for i in data['results'] if i.get('media_type') in ['movie', 'tv']][:8]
        if not items:
            bot.edit_message_text("ရုပ်ရှင်ရှာမတွေ့ပါ။", message.chat.id, status.message_id)
            return

        markup = InlineKeyboardMarkup()
        for i in items:
            title = i.get('title') or i.get('name')
            year = (i.get('release_date', 'N/A') or i.get('first_air_date', 'N/A'))[:4]
            markup.add(InlineKeyboardButton(f"🎬 {title} ({year})", callback_data=f"info_{i['media_type']}_{i['id']}"))
        
        bot.edit_message_text(f"🔍 '{search_query}' အတွက် ရလဒ်များ -", message.chat.id, status.message_id, reply_markup=markup)
    else:
        bot.edit_message_text("ရှာမတွေ့ပါ။", message.chat.id, status.message_id)

print("Bot is running with Groq AI...")
bot.polling(none_stop=True)