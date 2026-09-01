import logging
from datetime import datetime, timedelta
from aiogram import Bot
from config import CHANNEL_USERNAME, LOG_FILE

# লগিং সেটআপ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def check_channel_membership(bot: Bot, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {e}")
        return False

# সাধারণ অ্যান্টি-ফ্লাড (ইন-মেমোরি)
user_last_request = {}

async def anti_flood(user_id: int, limit: float = 1.0) -> bool:
    now = datetime.now()
    if user_id in user_last_request:
        last = user_last_request[user_id]
        if (now - last) < timedelta(seconds=limit):
            return False
    user_last_request[user_id] = now
    return True
