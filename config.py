import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram - Configuration dynamique selon le compte actif
    @property
    def TELEGRAM_API_ID(self):
        active_account = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "DID")
        return int(os.getenv(f"TELEGRAM_{active_account}_API_ID", "0"))
    
    @property
    def TELEGRAM_API_HASH(self):
        active_account = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "DID")
        return os.getenv(f"TELEGRAM_{active_account}_API_HASH", "")
    
    @property
    def TELEGRAM_SESSION_NAME(self):
        active_account = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "DID")
        return os.getenv(f"TELEGRAM_{active_account}_SESSION", f"{active_account}.session")
    
    # Trading
    TOTAL_RISK_EUR = float(os.getenv("TOTAL_RISK_EUR", "45.0"))
    MAX_RISK_PERCENTAGE = float(os.getenv("MAX_RISK_PERCENTAGE", "7.0"))
    GPT_KEY = os.getenv("GPT_KEY", "")
    
    # IDs des canaux
    TELEGRAM_CHANNEL_1_ID = int(os.getenv("TELEGRAM_CHANNEL_1_ID", "-2125503665"))
    TELEGRAM_CHANNEL_2_ID = int(os.getenv("TELEGRAM_CHANNEL_2_ID", "-2259371711"))
    
    # Comptes MT5 - Seulement DID et DEMO
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
        account_type = account_type.upper()
        
        print(f"🔧 DEBUG: get_mt5_credentials appelé pour {account_type}")
        
        if account_type == 'DID':
            login = self.MT5_DID_LOGIN
            password = self.MT5_DID_PASSWORD
            server = self.MT5_DID_SERVER
            print(f"🔧 DEBUG: DID - Login: '{login}', Password: '{password}', Server: '{server}'")
        elif account_type == 'DEMO':
            login = self.MT5_DEMO_LOGIN
            password = self.MT5_DEMO_PASSWORD
            server = self.MT5_DEMO_SERVER
            print(f"🔧 DEBUG: DEMO - Login: '{login}', Password: '{password}', Server: '{server}'")
        else:
            raise ValueError(f"Type de compte non supporté: {account_type}. Comptes disponibles: DID, DEMO")
        
        # Conversion du login en entier si présent
        login_int = None
        if login:
            try:
                login_int = int(login)
                print(f"🔧 DEBUG: Login converti en int: {login_int}")
            except ValueError:
                print(f"❌ DEBUG: Impossible de convertir le login '{login}' en entier")
        else:
            print(f"❌ DEBUG: Login vide pour {account_type}")
        
        result = {
            'login': login_int,
            'password': password,
            'server': server
        }
        
        print(f"🔧 DEBUG: Credentials finaux pour {account_type}: {result}")
        return result
    
    def get_telegram_credentials(self, account_type=None):
        """Retourne les identifiants Telegram selon le compte."""
        if account_type is None:
            account_type = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "DID")
        
        account_type = account_type.upper()
        
        return {
            'api_id': int(os.getenv(f"TELEGRAM_{account_type}_API_ID", "0")),
            'api_hash': os.getenv(f"TELEGRAM_{account_type}_API_HASH", ""),
            'session_name': os.getenv(f"TELEGRAM_{account_type}_SESSION", f"{account_type}.session")
        }

# Instance globale
config = Config()