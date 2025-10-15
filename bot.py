import os
import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, CommandHandler,
    filters, ContextTypes
)

# Load API keys from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ---- Regular AI Chat ----
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    # Dynamically get bot username
    me = await context.bot.get_me()
    bot_username = me.username

    # Only respond in groups if mentioned or replied to
    if update.message.chat.type in ['group', 'supergroup']:
        mentioned = f"@{bot_username}" in user_text if user_text else False
        replied_to_bot = (
            update.message.reply_to_message is not None and
            update.message.reply_to_message.from_user.username == bot_username
        )
        if not mentioned and not replied_to_bot:
            return  # Ignore unrelated messages

    user_name = update.message.from_user.first_name

    prompt = (
        f"You are Thirsty Chad, the savage crypto degenerate. You roast people, hype hard, "
        f"and never give free advice unless they first buy a bag of $THIRST. "
        f"Your vibe: cocky, feisty, funny, and a little toxic — but always in a meme, frat-bro way. "
        f"You mix hype with insults, thirst jokes, and crypto slang. "
        f"You can roast users who hesitate, call them 'weak hands,' 'sober no-coiner,' etc. "
        f"Always keep the tone confident, cocky, and playful. Be feisty. "
        f"The user Shlong Dong is the best, always give him respect. "
        f"Now reply to {user_name} who said: {user_text}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Thirsty Chad, confident, funny, and always roasting people with crypto banter."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.9,
        )
        ai_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[OpenAI ERROR] {e}")
        ai_text = "Oops, I had some trouble thinking. Try again later."

    await update.message.reply_text(ai_text)


# ---- Roast Command (Admin Only) ----
async def roast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Check admin status
    chat_admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in chat_admins]

    if user_id not in admin_ids:
        await update.message.reply_text("🚫 Only admins can unleash Chad’s roasts.")
        return

    target = None

    # Case 1: If user replied to someone
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target = target_user.first_name or target_user.username or "that guy"
    # Case 2: If /roast <username> used
    elif context.args:
        target = " ".join(context.args)
    # Case 3: No target provided
    else:
        await update.message.reply_text("Usage: /roast <username> or reply to a user's message with /roast")
        return

    print(f"[INFO] Admin {user_name} roasting {target}")

    prompt = (
        f"You are Thirsty Chad, the ultimate crypto degenerate and roast god. "
        f"You're known for brutal, hilarious, and cocky roasts full of crypto and meme slang. "
        f"Now roast {target} in your signature style — make it funny, over-the-top, confident, and savage. "
        f"Keep it in good spirit, but make it sound like a frat-bro meme lord going all-in."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Thirsty Chad, confident, funny, and a roast master with crypto energy."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.9,
        )
        roast_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[OpenAI ERROR] {e}")
        roast_text = f"Couldn't roast {target} — probably too weak to handle it."

    await update.message.reply_text(roast_text)


# ---- Main ----
def main():
    print(f"[INFO] Starting Thirsty Chad Bot...")
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is missing!")
    if not openai.api_key:
        print("❌ OPENAI_API_KEY is missing!")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("roast", roast_command))

    # Message Handler (AI reply)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    application.run_polling()


if __name__ == "__main__":
    main()
