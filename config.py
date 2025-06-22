import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram - Configuration pour DID uniquement
    @property
    def TELEGRAM_API_ID(self):
        return int(os.getenv("TELEGRAM_DID_API_ID", "0"))
    
    @property
    def TELEGRAM_API_HASH(self):
        return os.getenv("TELEGRAM_DID_API_HASH", "")
    
    @property
    def TELEGRAM_SESSION_NAME(self):
        return os.getenv("TELEGRAM_DID_SESSION", "DID.session")
    
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
        
        print(f"🔧 DEBUG Config: get_mt5_credentials appelé pour '{account_type}'")
        print(f"🔧 DEBUG Config: Attributs disponibles: {[attr for attr in dir(self) if 'MT5' in attr]}")
        
        if account_type == 'DID':
            print(f"🔧 DEBUG Config: Récupération credentials DID...")
            login = self.MT5_DID_LOGIN
            password = self.MT5_DID_PASSWORD
            server = self.MT5_DID_SERVER
            print(f"🔧 DEBUG Config: DID - Login: '{login}', Password: '{password}', Server: '{server}'")
        elif account_type == 'DEMO':
            print(f"🔧 DEBUG Config: Récupération credentials DEMO...")
            login = self.MT5_DEMO_LOGIN
            password = self.MT5_DEMO_PASSWORD
            server = self.MT5_DEMO_SERVER
            print(f"🔧 DEBUG Config: DEMO - Login: '{login}', Password: '{password}', Server: '{server}'")
        else:
            error_msg = f"Type de compte non supporté: {account_type}. Comptes disponibles: DID, DEMO"
            print(f"❌ DEBUG Config: {error_msg}")
            raise ValueError(error_msg)
        
        # Conversion du login en entier si présent
        login_int = None
        if login:
            try:
                login_int = int(login)
                print(f"🔧 DEBUG Config: Login converti en int: {login_int}")
            except ValueError:
                print(f"❌ DEBUG Config: Impossible de convertir le login '{login}' en entier")
        else:
            print(f"❌ DEBUG Config: Login vide pour {account_type}")
        
        result = {
            'login': login_int,
            'password': password,
            'server': server
        }
        
        print(f"🔧 DEBUG Config: Credentials finaux pour {account_type}: {result}")
        return result
    
    def get_telegram_credentials(self, account_type=None):
        """Retourne les identifiants Telegram pour DID."""
        print(f"🔧 DEBUG Config: get_telegram_credentials appelé avec account_type='{account_type}'")
        
        # Toujours utiliser DID
        return {
            'api_id': int(os.getenv("TELEGRAM_DID_API_ID", "0")),
            'api_hash': os.getenv("TELEGRAM_DID_API_HASH", ""),
            'session_name': os.getenv("TELEGRAM_DID_SESSION", "DID.session")
        }

# Instance globale
config = Config()