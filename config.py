import os

BOT_TOKEN = os.getenv("BOT_TOKEN")          # Render-এ Environment Variable থেকে নেবে
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "1604189136").split(",")]
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "usdt_repay")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1004343332067")) if os.getenv("CHANNEL_ID") else None
JOIN_BONUS = float(os.getenv("JOIN_BONUS", "5.0"))
REFERRAL_BONUS = float(os.getenv("REFERRAL_BONUS", "2.0"))
MIN_WITHDRAWAL = float(os.getenv("MIN_WITHDRAWAL", "10.0"))
DATABASE_FILE = os.getenv("DATABASE_FILE", "bot_database.db")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")
PORT = int(os.getenv("PORT", "8080"))
