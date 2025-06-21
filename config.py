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
    
    # Comptes MT5
    # Compte MAT
    MT5_MAT_LOGIN = os.getenv("MT5_MAT_LOGIN", "")
    MT5_MAT_PASSWORD = os.getenv("MT5_MAT_PASSWORD", "")
    MT5_MAT_SERVER = os.getenv("MT5_MAT_SERVER", "")
    
    # Compte DID
    MT5_DID_LOGIN = os.getenv("MT5_DID_LOGIN", "")
    MT5_DID_PASSWORD = os.getenv("MT5_DID_PASSWORD", "")
    MT5_DID_SERVER = os.getenv("MT5_DID_SERVER", "")
    
    # Compte DEMO
    MT5_DEMO_LOGIN = os.getenv("MT5_DEMO_LOGIN", "")
    MT5_DEMO_PASSWORD = os.getenv("MT5_DEMO_PASSWORD", "")
    MT5_DEMO_SERVER = os.getenv("MT5_DEMO_SERVER", "")
    
    def get_mt5_credentials(self, account_type):
        """Retourne les identifiants MT5 selon le type de compte."""
        if account_type.upper() == 'MAT':
            return {
                'login': int(self.MT5_MAT_LOGIN) if self.MT5_MAT_LOGIN else None,
                'password': self.MT5_MAT_PASSWORD,
                'server': self.MT5_MAT_SERVER
            }
        elif account_type.upper() == 'DID':
            return {
                'login': int(self.MT5_DID_LOGIN) if self.MT5_DID_LOGIN else None,
                'password': self.MT5_DID_PASSWORD,
                'server': self.MT5_DID_SERVER
            }
        elif account_type.upper() == 'DEMO':
            return {
                'login': int(self.MT5_DEMO_LOGIN) if self.MT5_DEMO_LOGIN else None,
                'password': self.MT5_DEMO_PASSWORD,
                'server': self.MT5_DEMO_SERVER
            }
        else:
            raise ValueError(f"Type de compte non supporté: {account_type}")

# Instance globale
config = Config()