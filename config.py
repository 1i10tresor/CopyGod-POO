import os
from dotenv import load_dotenv

class TelegramConfig:
    """
    Configuration des canaux Telegram.
    """
    
    def __init__(self):
        load_dotenv()
        
        # Configuration de l'API Telegram (compte utilisateur)
        self.API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
        self.API_HASH = os.getenv("TELEGRAM_API_HASH", "")
        self.SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "trading_bot_session")
        
        # IDs des canaux Telegram RÉELS
        self.CHANNEL_IDS = {
            1: int(os.getenv("TELEGRAM_CHANNEL_1_ID", "-2125503665")),  # Canal 1 - Format Standard
            2: int(os.getenv("TELEGRAM_CHANNEL_2_ID", "-2259371711"))   # Canal 2 - Format Fourchette
        }
        
        # Validation de la configuration
        self._validate_config()
    
    def _validate_config(self):
        """
        Valide la configuration Telegram.
        """
        missing_configs = []
        
        if not self.API_ID or self.API_ID == 0:
            missing_configs.append("TELEGRAM_API_ID")
        
        if not self.API_HASH:
            missing_configs.append("TELEGRAM_API_HASH")
        
        if missing_configs:
            print("⚠️  Configuration Telegram incomplète:")
            for config in missing_configs:
                print(f"   - {config} manquant dans .env")
            print("\n💡 Ajoutez ces variables dans votre fichier .env")
    
    def get_channel_id(self, channel_number):
        """
        Récupère l'ID Telegram d'un canal.
        
        Args:
            channel_number (int): Numéro du canal (1 ou 2)
        
        Returns:
            int: ID du canal Telegram
        """
        return self.CHANNEL_IDS.get(channel_number)
    
    def get_channel_name(self, channel_number):
        """
        Récupère le nom d'un canal.
        
        Args:
            channel_number (int): Numéro du canal
        
        Returns:
            str: Nom du canal
        """
        names = {
            1: "Canal Standard (3 TPs)",
            2: "Canal Fourchette (3 Entrées)"
        }
        return names.get(channel_number, f"Canal {channel_number}")
    
    def display_config(self):
        """
        Affiche la configuration actuelle.
        """
        print("\n" + "=" * 60)
        print("CONFIGURATION TELEGRAM")
        print("=" * 60)
        
        print(f"API ID: {'✅ Configuré' if self.API_ID else '❌ Manquant'}")
        print(f"API Hash: {'✅ Configuré' if self.API_HASH else '❌ Manquant'}")
        print(f"Session: {self.SESSION_NAME}")
        
        print("\nCanaux surveillés:")
        for channel_num, channel_id in self.CHANNEL_IDS.items():
            channel_name = self.get_channel_name(channel_num)
            print(f"  📡 Canal {channel_num}: {channel_name}")
            print(f"      ID Telegram: {channel_id}")
        
        print("=" * 60 + "\n")


class TradingConfig:
    """
    Configuration du système de trading.
    """
    
    def __init__(self):
        load_dotenv()
        
        # Configuration des risques
        self.TOTAL_RISK_EUR = float(os.getenv("TOTAL_RISK_EUR", "300.0"))
        self.MAX_RISK_PERCENTAGE = float(os.getenv("MAX_RISK_PERCENTAGE", "7.0"))
        
        # Configuration ChatGPT
        self.GPT_KEY = os.getenv("GPT_KEY", "")
        
        # Configuration MT5
        self.MT5_LOGIN = os.getenv("MT5_LOGIN", "")
        self.MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
        self.MT5_SERVER = os.getenv("MT5_SERVER", "")
        
        # Validation
        self._validate_config()
    
    def _validate_config(self):
        """
        Valide la configuration de trading.
        """
        if not self.GPT_KEY:
            print("⚠️  GPT_KEY manquant dans .env")
        
        if not all([self.MT5_LOGIN, self.MT5_PASSWORD, self.MT5_SERVER]):
            print("⚠️  Configuration MT5 incomplète dans .env")
    
    def display_config(self):
        """
        Affiche la configuration de trading.
        """
        print("\n" + "=" * 60)
        print("CONFIGURATION TRADING")
        print("=" * 60)
        
        print(f"Risque total par signal: {self.TOTAL_RISK_EUR} EUR")
        print(f"Limite de risque compte: {self.MAX_RISK_PERCENTAGE}%")
        print(f"ChatGPT: {'✅ Configuré' if self.GPT_KEY else '❌ Manquant'}")
        print(f"MT5: {'✅ Configuré' if all([self.MT5_LOGIN, self.MT5_PASSWORD, self.MT5_SERVER]) else '❌ Incomplet'}")
        
        print("=" * 60 + "\n")


# Configuration globale
telegram_config = TelegramConfig()
trading_config = TradingConfig()

# Exemple de fichier .env
ENV_EXAMPLE = """
# Configuration Telegram - Comptes utilisateurs
TELEGRAM_API_ID=26513066
TELEGRAM_API_HASH=6c3198f742f9f01de443990154353d95
TELEGRAM_SESSION_NAME=trading_bot_session
TELEGRAM_CHANNEL_1_ID=-2125503665
TELEGRAM_CHANNEL_2_ID=-2259371711

# Configuration Trading
TOTAL_RISK_EUR=300.0
MAX_RISK_PERCENTAGE=7.0
GPT_KEY=your_openai_api_key_here

# Configuration MT5
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server
"""

if __name__ == "__main__":
    # Afficher la configuration actuelle
    telegram_config.display_config()
    trading_config.display_config()
    
    # Afficher l'exemple de .env
    print("📝 EXEMPLE DE FICHIER .env:")
    print("=" * 60)
    print(ENV_EXAMPLE)