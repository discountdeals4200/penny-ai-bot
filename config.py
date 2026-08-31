import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///penny_bot.db")

# Retail Websites
TARGET_WEBSITES = os.getenv("TARGET_WEBSITES", "amazon.com,walmart.com").split(",")

# Bot Settings
MAX_PRICE_THRESHOLD = float(os.getenv("MAX_PRICE_THRESHOLD", "1.00"))
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", "60"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Notification Settings
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Logging
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"
