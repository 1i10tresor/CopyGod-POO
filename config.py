import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "trading_bot_session")
    
    # Trading
    TOTAL_RISK_EUR = float(os.getenv("TOTAL_RISK_EUR", "300.0"))
    MAX_RISK_PERCENTAGE = float(os.getenv("MAX_RISK_PERCENTAGE", "7.0"))
    GPT_KEY = os.getenv("GPT_KEY", "")
    
    # MT5
    MT5_LOGIN = os.getenv("MT5_LOGIN", "")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "")

# Instance globale
config = Config()