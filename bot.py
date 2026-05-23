import telebot
import os
import requests
import time
import os
TOKEN = os.environ.get("TOKEN","8907709500:AAGucJQj2wmCECeqadO5-HRk8N9c4W1GAfo")
WEATHER_KEY = os.environ.get("WEATHER_TOKEN","92a87062034410072bbc50805706f2c2")
GIPHY_KEY = os.environ.get("GIPHY_KEY","XCZUVYIhpSfOZLs2zSVFYiu1LopTFs5q")


bot = telebot.TeleBot(TOKEN)

user_lang = {}
user_step = {}  # "lang" yoki "city"

texts = {
    "uz": {
        "chosen": "✅ O'zbek tili tanlandi!",
        "ask_city": "🌍 Qaysi shahar ob-havosini bilmoqchisiz?",
        "not_found": "❌ Shahar topilmadi! To'g'ri yozing.",
        "next": "📍 Boshqa shahar? Nomini yozing!",
        "result": "🌍 Shahar: {}\n🌡 Harorat: {}°C\n🌤 Havo: {}\n💨 Shamol: {} m/s\n💧 Namlik: {}%"
    },
    "ru": {
        "chosen": "✅ Русский язык выбран!",
        "ask_city": "🌍 Какой город вас интересует?",
        "not_found": "❌ Город не найден!",
        "next": "📍 Другой город? Напишите!",
        "result": "🌍 Город: {}\n🌡 Температура: {}°C\n🌤 Погода: {}\n💨 Ветер: {} м/с\n💧 Влажность: {}%"
    },
    "en": {
        "chosen": "✅ English selected!",
        "ask_city": "🌍 Which city weather do you want?",
        "not_found": "❌ City not found!",
        "next": "📍 Another city? Write the name!",
        "result": "🌍 City: {}\n🌡 Temp: {}°C\n🌤 Weather: {}\n💨 Wind: {} m/s\n💧 Humidity: {}%"
    }
}

def get_weather(city, lang="uz"):
    api_lang = "uz" if lang=="uz" else "ru" if lang=="ru" else "en"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang={api_lang}"
    r = requests.get(url).json()
    if r.get("cod") != 200:
        return None, None
    name = r["name"]
    temp = round(r["main"]["temp"])
    desc = r["weather"][0]["description"]
    wind = r["wind"]["speed"]
    hum = r["main"]["humidity"]
    condition = r["weather"][0]["main"].lower()
    return texts[lang]["result"].format(name, temp, desc, wind, hum), condition

def get_gif(keyword):
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_KEY}&q={keyword}+weather&limit=1&rating=g"
    r = requests.get(url).json()
    try:
        return r["data"][0]["images"]["original"]["url"]
    except:
        return None

@bot.message_handler(commands=["start"])
def start(message):
    cid = str(message.chat.id)
    name = message.from_user.first_name or "Foydalanuvchi"
    user_step[cid] = "lang"
    user_lang[cid] = None

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English")
    bot.send_message(message.chat.id, f"👋 Salom, {name}!\nTilni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_step.get(str(m.chat.id)) == "lang")
def choose_lang(message):
    cid = str(message.chat.id)
    txt = message.text

    if "O'zbek" in txt:
        user_lang[cid] = "uz"
    elif "Русский" in txt:
        user_lang[cid] = "ru"
    elif "English" in txt:
        user_lang[cid] = "en"
    else:
        bot.send_message(message.chat.id, "Iltimos tugmadan tanlang!")
        return

    user_step[cid] = "city"
    lang = user_lang[cid]
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, texts[lang]["chosen"], reply_markup=markup)
    bot.send_message(message.chat.id, texts[lang]["ask_city"])

@bot.message_handler(func=lambda m: user_step.get(str(m.chat.id)) == "city")
def handle_city(message):
    cid = str(message.chat.id)
    lang = user_lang.get(cid, "uz")
    txt = message.text

    result, condition = get_weather(txt, lang)
    if result is None:
        bot.send_message(message.chat.id, texts[lang]["not_found"])
        return

    bot.send_message(message.chat.id, result)

    if condition:
        gif_url = get_gif(condition)
        if gif_url:
            bot.send_animation(message.chat.id, gif_url)

    bot.send_message(message.chat.id, texts[lang]["next"])

@bot.message_handler(func=lambda m: user_step.get(str(m.chat.id)) is None)
def no_start(message):
    bot.send_message(message.chat.id, "Iltimos /start bosing!")

print("Bot ishga tushdi!")
bot.polling(none_stop=True)
