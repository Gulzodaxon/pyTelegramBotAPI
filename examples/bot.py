import telebot
import wikipedia
import sqlite3

API_TOKEN = '7260819449:AAGsz-PZKMnSsgqMs2hyc-qziCj0wXK5h7M'
bot = telebot.TeleBot(API_TOKEN)
wikipedia.set_lang("uz")

# Baza
conn = sqlite3.connect("projects.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS projects (
    user_id INTEGER,
    project_text TEXT
)
""")
conn.commit()

# Foydalanuvchi holati
user_states = {}

# /start komandasi
@bot.message_handler(commands=['start'])
def start_handler(message):
    user = message.from_user
    user_id = user.id
    full_name = user.first_name
    username = user.username

    print(f"start bosgan foydalanuvchi: {full_name} (@{username}), ID: {user_id}")
    bot.reply_to(message, f"Salom, {full_name}! Botga xush kelibsiz 👋. Wikipediyadan qidirilishi kerak bo'lgan narsani kiriting")

# /help komandasi
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, "<b>Wikipedia</b> dan qidirilishi kerak bo'lgan savolni kiriting!", parse_mode="HTML")

# /createproject komandasi
@bot.message_handler(commands=['createproject'])
def create_project(message):
    user_states[message.from_user.id] = 'waiting_for_project'
    bot.reply_to(message, "Arizangiz qabul qilindi. Endi loyiha haqida xabar yuboring.")

# /myproject komandasi
@bot.message_handler(commands=['myproject'])
def my_project(message):
    user_id = message.from_user.id
    cur.execute("SELECT project_text FROM projects WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    if rows:
        bot.send_message(message.chat.id, "Sizning loyihalaringiz:")
        for row in rows:
            bot.send_message(message.chat.id, f"📌 {row[0]}")
    else:
        bot.send_message(message.chat.id, "Sizda hali hech qanday loyiha mavjud emas.")

# Matnli xabarlar uchun handler
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    user_id = message.from_user.id
    if user_states.get(user_id) == 'waiting_for_project':
        project_text = message.text
        cur.execute("INSERT INTO projects (user_id, project_text) VALUES (?, ?)", (user_id, project_text))
        conn.commit()
        user_states[user_id] = None
        bot.send_message(message.chat.id, "✅ Loyiha saqlandi.")
    else:
        try:
            result = wikipedia.summary(message.text)
            bot.send_message(message.chat.id, result)
        except:
            bot.send_message(message.chat.id, "Bu mavzuga oid maqola topilmadi.")

# Botni ishga tushirish
bot.polling(none_stop=True)
