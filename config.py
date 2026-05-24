import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DB_CONFIG = {
    'user': os.getenv("DB_USER", "nipohelp_user"),
    'password': os.getenv("DB_PASSWORD", "nipohelp_pass_2024"),
    'database': os.getenv("DB_NAME", "nipohelp_db"),
    'host': os.getenv("DB_HOST", "localhost"),
    'port': int(os.getenv("DB_PORT", "5432"))
}

MAX_DESCRIPTION_LEN = int(os.getenv("MAX_DESCRIPTION_LEN", "200"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN در فایل .env پیدا نشد!")
if ADMIN_ID == 0:
    raise ValueError("❌ ADMIN_ID در فایل .env پیدا نشد!")