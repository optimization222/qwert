import os
import json
import time
import threading
import requests
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === ТОКЕН И ID ГРУППЫ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_ID = int(os.environ.get("GROUP_ID", 0))

if not BOT_TOKEN or GROUP_ID == 0:
    raise ValueError("❌ BOT_TOKEN или GROUP_ID не заданы!")

# === НАСТРОЙКИ (ФАЙЛ) ===
SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "welcome_text": "Добро пожаловать в группу, {name}! 👋\nНапиши /help, чтобы узнать команды."
    }

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

settings = load_settings()

# === ПОЛНЫЙ СПИСОК МАТОВ ===
BAD_WORDS = [
    "хуй", "хуя", "хуё", "хуи", "хуйня", "хуйню", "хуйне", "хуйней",
    "пизда", "пизду", "пиздой", "пизде", "пиздец", "пиздос",
    "бля", "блять", "блядь", "блядский", "блядство",
    "ёб", "ёба", "ёбну", "ёбнул", "ёбнутый", "ёбарь", "ёбанный",
    "мудак", "мудаки", "мудачье", "мудозвон",
    "гандон", "гандону", "гандонский",
    "пидор", "пидорас", "пидорасы", "пидорский",
    "педик", "педики", "педикуша",
    "ебалай", "ебалайка", "ебанашка", "ебанат", "ебаный",
    "залупа", "залупка",
    "хуйло", "хуйла", "хуйлу", "хуйлом",
    "чмо", "чмовка", "чморыга",
    "урод", "уроды", "уродский",
    "выродок", "выродки",
    "тварь", "твари", "тварюга",
    "сука", "суки", "сучка", "сучонок",
    "шлюха", "шлюхи", "шлюшка",
    "курва", "курвиный",
    "мразь", "мрази", "мразотный",
    "гад", "гады", "гадина", "гадёныш",
    "сволочь", "сволочи", "сволочной",
    "дрянь", "дряни", "дрянной",
    "паскуда", "паскудный",
    "негодяй", "негодяи", "негодный",
    "подлец", "подлая", "подлый",
    "стерва", "стервоза",
    "засранец", "засранка",
    "обосранный", "обосрыш",
    "пердун", "пердунья",
    "вонючка", "вонючий",
    "мудила", "мудило", "мудильщик",
    "петух", "петушиный", "петушара",
    "анальный", "анально", "анал",
    "оральный", "орально",
    "секс", "сексуальный",
    "минет", "минетчик",
    "куни", "кунилингус",
    "групповуха", "групповой_секс",
    "порно", "порнуха", "порнография",
    "свинг", "свингеры",
    "бдсм", "бондаж",
    "жопа", "жопой", "жопный", "жопка",
    "очко", "очковый",
    "жополиз", "жополизный",
    "срака", "сраку", "срать", "срал", "срач",
    "засрать", "засрал", "засранный",
    "опорожниться", "понос", "диарея",
    "иди_нахуй", "пошёл_нахуй", "нахуй_иди",
    "хуй_тебе", "хуй_вам", "хуй_на",
    "ебать_твою_мать", "ебать_в_рот", "ебать_мозг",
    "ёб_твою_мать", "ёб_в_рот",
    "пиздец_полный", "пиздец_наступил",
    "блядство_какое", "блядский_ад",
    "мудак_конченый", "мудачье_сборище",
    "гандон_вонючий",
    "пидорас_недоделанный",
    "педик_голубой",
    "чмо_ебаное",
    "урод_конченый",
    "тварь_бесстыжая",
    "сука_блядская",
    "шлюха_дешёвая",
    "мразь_человеческая",
    "гад_ползучий",
    "сволочь_бездарная",
    "дрянь_ничтожная",
    "паскуда_грязная",
    "негодяй_редкий",
    "подлец_последний",
    "стерва_ненасытная",
    "засранец_наглый",
    "обосранный_пингвин",
    "пердун_вонючий",
    "кринж", "кринжовый",
    "дегенерат", "деградант",
    "имбецил", "олигофрен",
    "дурак_дремучий",
    "дебил_конченый",
    "идиот_конченый",
    "кретин", "кретиноид",
    "псих", "психуй",
    "шиз", "шизофреник",
    "параноик",
    "депрессняк", "депресняк",
    "тоска_зелёная",
    "скука_смертельная",
    "в_сраку_такую_жизнь",
    "жизнь_боль",
    "счастья_нет",
    "ну_и_ну",
    "поехавший",
    "кукуха_поехала",
    "крыша_поехала",
    "сдвинутый_на_голову",
    "жопошник",
    "членоглот",
    "членоноситель",
    "пенис_носитель",
    "xya", "xyu", "xyй", "xйня", "xуй", "xуйн",
    "п3зда", "п3зд", "пiзда", "пiзд",
    "бл#$ть", "бл&ть", "бл@ть",
    "eбать", "eбaть", "eб@ть",
    "г@ндон", "г#ндон", "г&ндон",
    "пiдор", "п#дор", "п&дор",
    "м@дак", "м#дак", "м&дак"
]

# === ПРОВЕРКА АДМИНА ===
async def is_admin_or_owner(update: Update) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    try:
        member = await update.get_bot().get_chat_member(chat_id, user_id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

# === ПРИВЕТСТВИЕ ===
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        name = member.full_name or member.username or "участник"
        text = settings.get("welcome_text", "Добро пожаловать, {name}!").format(name=name)
        await update.message.reply_text(text)

# === СМЕНА ПРИВЕТСТВИЯ ===
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update):
        await update.message.reply_text("⛔ Только для админов.")
        return

    if not context.args:
        await update.message.reply_text("ℹ️ /set_welcome Твой текст с {name}")
        return

    new_text = " ".join(context.args)
    settings["welcome_text"] = new_text
    save_settings(settings)
    await update.message.reply_text(f"✅ Приветствие обновлено:\n{new_text}")

# === ПОКАЗАТЬ ПРИВЕТСТВИЕ ===
async def show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update):
        await update.message.reply_text("⛔ Только для админов.")
        return
    text = settings.get("welcome_text", "Добро пожаловать, {name}!")
    await update.message.reply_text(f"📌 Текущее приветствие:\n{text}")

# === /GETID ===
async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 ID этой группы: `{update.effective_chat.id}`")

# === /HELP ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот для группы\n"
        "/set_welcome текст — сменить приветствие (с {name})\n"
        "/show_welcome — показать текущее\n"
        "/getid — узнать ID группы\n"
        "/help — это сообщение"
    )

# === МОДЕРАЦИЯ МАТА ===
async def moderate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return

    text = update.message.text
    if not text:
        return

    lower_text = text.lower().replace(" ", "").replace("_", "").replace("@", "")

    for word in BAD_WORDS:
        clean_word = word.replace("_", "").replace(" ", "")
        if clean_word in lower_text:
            await update.message.delete()
            await update.message.reply_text("🚫 Не матерись!")
            return

# === ПИНГ ДЛЯ RENDER ===
def keep_alive():
    url = os.environ.get("RENDER_EXTERNAL_URL", "https://qwer-bot.onrender.com")
    while True:
        try:
            requests.get(url)
        except:
            pass
        time.sleep(600)

# === ЗАПУСК ===
if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", help_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("set_welcome", set_welcome))
    app.add_handler(CommandHandler("show_welcome", show_welcome))
    app.add_handler(CommandHandler("getid", get_group_id))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), moderate_message))

    print("🍋 Бот запущен и готов к работе!")
    app.run_polling()