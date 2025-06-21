import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram - Configuration dynamique selon le compte actif
    @property
    def TELEGRAM_API_ID(self):
        active_account = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "MAT")
        return int(os.getenv(f"TELEGRAM_{active_account}_API_ID", "0"))
    
    @property
    def TELEGRAM_API_HASH(self):
        active_account = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "MAT")
        return os.getenv(f"TELEGRAM_{active_account}_API_HASH", "")
    
    @property
    def TELEGRAM_SESSION_NAME(self):
        active_account = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "MAT")
        return os.getenv(f"TELEGRAM_{active_account}_SESSION", f"{active_account}.session")
    
    # Trading
    TOTAL_RISK_EUR = float(os.getenv("TOTAL_RISK_EUR", "45.0"))
    MAX_RISK_PERCENTAGE = float(os.getenv("MAX_RISK_PERCENTAGE", "7.0"))
    GPT_KEY = os.getenv("GPT_KEY", "")
    
    # IDs des canaux
    TELEGRAM_CHANNEL_1_ID = int(os.getenv("TELEGRAM_CHANNEL_1_ID", "-2125503665"))
    TELEGRAM_CHANNEL_2_ID = int(os.getenv("TELEGRAM_CHANNEL_2_ID", "-2259371711"))
    
    # Comptes MT5
    # Compte MAT
    MT5_MAT_LOGIN = os.getenv("MT5_MAT_LOGIN", "")
    MT5_MAT_PASSWORD = os.getenv("MT5_MAT_MDP", "")
    MT5_MAT_SERVER = os.getenv("MT5_MAT_SERVEUR", "")
    
    # Compte DID
    MT5_DID_LOGIN = os.getenv("MT5_DID_LOGIN", "")
    MT5_DID_PASSWORD = os.getenv("MT5_DID_MDP", "")
    MT5_DID_SERVER = os.getenv("MT5_DID_SERVEUR", "")
    
    # Compte DEMO
    MT5_DEMO_LOGIN = os.getenv("MT5_DEMO_LOGIN", "")
    MT5_DEMO_PASSWORD = os.getenv("MT5_DEMO_MDP", "")
    MT5_DEMO_SERVER = os.getenv("MT5_DEMO_SERVEUR", "")
    
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
    
    def get_telegram_credentials(self, account_type=None):
        """Retourne les identifiants Telegram selon le compte."""
        if account_type is None:
            account_type = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "MAT")
        
        account_type = account_type.upper()
        
        return {
            'api_id': int(os.getenv(f"TELEGRAM_{account_type}_API_ID", "0")),
            'api_hash': os.getenv(f"TELEGRAM_{account_type}_API_HASH", ""),
            'session_name': os.getenv(f"TELEGRAM_{account_type}_SESSION", f"{account_type}.session")
        }

# Instance globale
config = Config()