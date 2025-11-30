# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 08:55:15 2025

@author: edu9481488
"""

import logging
import random
from telegram import Update , InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters,
    ContextTypes
    )

# Global Endring
games = {}   #game_id - {"players": set, "active" : bool, "current_word": str}
WORDS_FILE = "words.txt"

#Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Words loading
def load_words():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [w.strip() for w in f.readlines() if w.strip()]
    
    words = load_words()

# command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я бот для гри в слова. "
        "Почни гру командою /start_game"
        )
#command /start_game
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    games[chat_id] = {
        "players": set(),
        "active": False,
        "current_word" : None
        }
    keyboard = [
        [InlineKeyboardButton("🔵 JOIN", callback_data=f"join_{chat_id}")],
        [InlineKeyboardButton("❌ End Game", callback_data=f"end_{chat_id}")]
    ]

    await update.message.reply_text(
        "🎮 Гру запущено!\n"
        "Натисни JOIN, щоб приєднатися.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# -------------------
#   JOIN ↪️
# -------------------
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    user = update.effective_user

    if chat_id not in games:
        return

    games[chat_id]["players"].add(user.id)

    await update.callback_query.answer("Ти в грі!")
    await update.callback_query.edit_message_text(
        f"Гравців у грі: {len(games[chat_id]['players'])}\n"
        "Очікуємо інших…\n"
        "Натисніть END GAME щоб зупинити.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔵 JOIN", callback_data=f"join_{chat_id}")],
            [InlineKeyboardButton("❌ End Game", callback_data=f"end_{chat_id}")]
        ])
    )

    # якщо 2+ гравців – запускаємо гру
    if len(games[chat_id]["players"]) >= 2 and not games[chat_id]["active"]:
        await start_round(update, context, chat_id)

# -------------------
#   ЗАПУСК РАУНДУ
# -------------------
async def start_round(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    games[chat_id]["active"] = True
    word = random.choice(words)
    games[chat_id]["current_word"] = word

    await context.bot.send_message(
        chat_id,
        f"🟩 Новий раунд!\nНапишіть наступне слово :\n\n👉 *{word}*",
        parse_mode="Markdown"
    )


# -------------------
#   END GAME ❌
# -------------------
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    if chat_id in games:
        del games[chat_id]

    await update.callback_query.answer("Гру завершено")
    await update.callback_query.edit_message_text("❌ Гру завершено.")

# -------------------
#   ОБРОБНИК КНОПОК
# -------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data.startswith("join_"):
        chat_id = int(data.split("_")[1])
        await join_game(update, context, chat_id)

    elif data.startswith("end_"):
        chat_id = int(data.split("_")[1])
        await end_game(update, context, chat_id)

# -------------------
#   ОБРОБКА СЛІВ
# -------------------
async def handle_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in games or not games[chat_id]["active"]:
        return

    user_word = update.message.text.lower().strip()
    current = games[chat_id]["current_word"]

    if not current:
        return

    # перевірка остання буква → перша буква
    if user_word.startswith(current[-1]):
        games[chat_id]["current_word"] = user_word
        await update.message.reply_text(
            f"✅ Добре!\nНаступна літера: *{user_word[-1]}*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ Неправильно!\nСлово має починатися на: *{current[-1]}*",
            parse_mode="Markdown"
            )
# -------------------
#   MAIN
# -------------------
def main():
    TOKEN = "8456245702:AAGPsNAmtJ_w7b-2i_3Rc8b2E9KNAQeMbMA"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_game", start_game))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # новий обробник тексту
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_word))

    print("Бот запущений!")
    app.run_polling()


if __name__ == "__main__":
    main()