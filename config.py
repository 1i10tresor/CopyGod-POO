import os
from dotenv import load_dotenv

class TelegramConfig:
    """
    Configuration des canaux Telegram.
    """
    
    def __init__(self):
        load_dotenv()
        
        # Configuration de l'API Telegram (compte utilisateur) - VOS NOMS DE CLÉS
        self.API_ID = int(os.getenv("TELEGRAM_MAT_API_ID", "0"))
        self.API_HASH = os.getenv("TELEGRAM_MAT_API_HASH", "")
        self.SESSION_NAME = os.getenv("TELEGRAM_MAT_SESSION", "MAT.session")
        
        # IDs des canaux Telegram RÉELS
        self.CHANNEL_IDS = {
            1: int(os.getenv("TELEGRAM_CHANNEL_1_ID", "-2125503665")),  # Canal 1 - Format Standard
            2: int(os.getenv("TELEGRAM_CHANNEL_2_ID", "-2259371711"))   # Canal 2 - Format Fourchette
        }
        
        # Configuration avancée Telegram
        self.CONNECTION_RETRIES = int(os.getenv("TELEGRAM_CONNECTION_RETRIES", "3"))
        self.FLOOD_SLEEP_THRESHOLD = int(os.getenv("TELEGRAM_FLOOD_SLEEP_THRESHOLD", "60"))
        self.TIMEOUT = int(os.getenv("TELEGRAM_TIMEOUT", "30"))
        
        # Validation de la configuration
        self._validate_config()
    
    def _validate_config(self):
        """
        Valide la configuration Telegram.
        """
        missing_configs = []
        
        if not self.API_ID or self.API_ID == 0:
            missing_configs.append("TELEGRAM_MAT_API_ID")
        
        if not self.API_HASH:
            missing_configs.append("TELEGRAM_MAT_API_HASH")
        
        if missing_configs:
            print("⚠️  Configuration Telegram incomplète:")
            for config in missing_configs:
                print(f"   - {config} manquant dans .env")
            print("\n💡 Ajoutez ces variables dans votre fichier .env")
            print("📋 Obtenez vos clés sur: https://my.telegram.org/apps")
    
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
    
    def get_all_channel_ids(self):
        """
        Retourne tous les IDs de canaux surveillés.
        
        Returns:
            list: Liste des IDs Telegram
        """
        return list(self.CHANNEL_IDS.values())
    
    def is_valid_config(self):
        """
        Vérifie si la configuration est valide.
        
        Returns:
            bool: True si configuration complète
        """
        return bool(self.API_ID and self.API_ID != 0 and self.API_HASH)
    
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
        print(f"Tentatives de connexion: {self.CONNECTION_RETRIES}")
        print(f"Timeout: {self.TIMEOUT}s")
        
        print("\nCanaux surveillés:")
        for channel_num, channel_id in self.CHANNEL_IDS.items():
            channel_name = self.get_channel_name(channel_num)
            print(f"  📡 Canal {channel_num}: {channel_name}")
            print(f"      ID Telegram: {channel_id}")
        
        if not self.is_valid_config():
            print("\n⚠️  ATTENTION: Configuration incomplète!")
            print("💡 Ajoutez vos clés API dans le fichier .env")
        
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
        self.GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4-turbo")
        self.GPT_TIMEOUT = int(os.getenv("GPT_TIMEOUT", "30"))
        
        # Configuration MT5 - VOS NOMS DE CLÉS
        self.MT5_LOGIN = os.getenv("MT5_DEMO_LOGIN", "")
        self.MT5_PASSWORD = os.getenv("MT5_DEMO_MDP", "")
        self.MT5_SERVER = os.getenv("MT5_DEMO_SERVEUR", "")
        
        # Configuration avancée MT5
        self.MT5_TIMEOUT = int(os.getenv("MT5_TIMEOUT", "60000"))  # en millisecondes
        self.MT5_DEVIATION = int(os.getenv("MT5_DEVIATION", "20"))
        self.MT5_MAGIC_BASE = int(os.getenv("MT5_MAGIC_BASE", "234000"))
        
        # Configuration des ordres
        self.ORDER_RETRY_COUNT = int(os.getenv("ORDER_RETRY_COUNT", "3"))
        self.ORDER_RETRY_DELAY = float(os.getenv("ORDER_RETRY_DELAY", "1.0"))
        
        # Configuration de logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"
        self.LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "trading_bot.log")
        
        # Validation
        self._validate_config()
    
    def _validate_config(self):
        """
        Valide la configuration de trading.
        """
        issues = []
        
        # Vérifier ChatGPT
        if not self.GPT_KEY:
            issues.append("GPT_KEY manquant")
        elif not self.GPT_KEY.startswith('sk-'):
            issues.append("GPT_KEY semble invalide (doit commencer par 'sk-')")
        
        # Vérifier MT5
        mt5_missing = []
        if not self.MT5_LOGIN:
            mt5_missing.append("MT5_DEMO_LOGIN")
        if not self.MT5_PASSWORD:
            mt5_missing.append("MT5_DEMO_MDP")
        if not self.MT5_SERVER:
            mt5_missing.append("MT5_DEMO_SERVEUR")
        
        if mt5_missing:
            issues.append(f"Configuration MT5 incomplète: {', '.join(mt5_missing)}")
        
        # Vérifier les valeurs de risque
        if self.TOTAL_RISK_EUR <= 0:
            issues.append("TOTAL_RISK_EUR doit être > 0")
        
        if self.MAX_RISK_PERCENTAGE <= 0 or self.MAX_RISK_PERCENTAGE > 100:
            issues.append("MAX_RISK_PERCENTAGE doit être entre 0 et 100")
        
        # Afficher les problèmes
        if issues:
            print("⚠️  PROBLÈMES DE CONFIGURATION:")
            for issue in issues:
                print(f"   - {issue}")
            print()
    
    def is_mt5_configured(self):
        """
        Vérifie si MT5 est correctement configuré.
        
        Returns:
            bool: True si MT5 est configuré
        """
        return all([self.MT5_LOGIN, self.MT5_PASSWORD, self.MT5_SERVER])
    
    def is_gpt_configured(self):
        """
        Vérifie si ChatGPT est correctement configuré.
        
        Returns:
            bool: True si ChatGPT est configuré
        """
        return bool(self.GPT_KEY and self.GPT_KEY.startswith('sk-'))
    
    def get_mt5_credentials(self):
        """
        Retourne les identifiants MT5.
        
        Returns:
            dict: Dictionnaire avec login, password, server
        """
        return {
            'login': self.MT5_LOGIN,
            'password': self.MT5_PASSWORD,
            'server': self.MT5_SERVER
        }
    
    def display_config(self):
        """
        Affiche la configuration de trading.
        """
        print("\n" + "=" * 60)
        print("CONFIGURATION TRADING")
        print("=" * 60)
        
        # Configuration des risques
        print("💰 GESTION DES RISQUES:")
        print(f"  Risque total par signal: {self.TOTAL_RISK_EUR} EUR")
        print(f"  Limite de risque compte: {self.MAX_RISK_PERCENTAGE}%")
        print(f"  Risque par position: {self.TOTAL_RISK_EUR/3:.2f} EUR")
        
        # Configuration ChatGPT
        print("\n🤖 CHATGPT:")
        gpt_status = "✅ Configuré" if self.is_gpt_configured() else "❌ Manquant/Invalide"
        print(f"  Statut: {gpt_status}")
        print(f"  Modèle: {self.GPT_MODEL}")
        print(f"  Timeout: {self.GPT_TIMEOUT}s")
        
        # Configuration MT5
        print("\n📈 METATRADER 5:")
        mt5_status = "✅ Configuré" if self.is_mt5_configured() else "❌ Incomplet"
        print(f"  Statut: {mt5_status}")
        if self.is_mt5_configured():
            print(f"  Login: {self.MT5_LOGIN}")
            print(f"  Serveur: {self.MT5_SERVER}")
            print(f"  Timeout: {self.MT5_TIMEOUT}ms")
            print(f"  Déviation: {self.MT5_DEVIATION} points")
        
        # Configuration des ordres
        print("\n📋 ORDRES:")
        print(f"  Tentatives: {self.ORDER_RETRY_COUNT}")
        print(f"  Délai entre tentatives: {self.ORDER_RETRY_DELAY}s")
        print(f"  Magic number base: {self.MT5_MAGIC_BASE}")
        
        # Configuration de logging
        print("\n📝 LOGGING:")
        print(f"  Niveau: {self.LOG_LEVEL}")
        print(f"  Fichier: {'✅ Activé' if self.LOG_TO_FILE else '❌ Désactivé'}")
        if self.LOG_TO_FILE:
            print(f"  Chemin: {self.LOG_FILE_PATH}")
        
        print("=" * 60 + "\n")


class SystemConfig:
    """
    Configuration globale du système.
    """
    
    def __init__(self):
        load_dotenv()
        
        # Mode de fonctionnement
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"
        
        # Configuration de performance
        self.MAX_CONCURRENT_SIGNALS = int(os.getenv("MAX_CONCURRENT_SIGNALS", "5"))
        self.MESSAGE_PROCESSING_DELAY = float(os.getenv("MESSAGE_PROCESSING_DELAY", "0.5"))
        
        # Configuration de sécurité
        self.ENABLE_RISK_CHECKS = os.getenv("ENABLE_RISK_CHECKS", "true").lower() == "true"
        self.ENABLE_SIGNAL_VALIDATION = os.getenv("ENABLE_SIGNAL_VALIDATION", "true").lower() == "true"
        
        # Sauvegarde et historique
        self.SAVE_SIGNALS_HISTORY = os.getenv("SAVE_SIGNALS_HISTORY", "true").lower() == "true"
        self.HISTORY_FILE_PATH = os.getenv("HISTORY_FILE_PATH", "signals_history.json")
        self.MAX_HISTORY_ENTRIES = int(os.getenv("MAX_HISTORY_ENTRIES", "1000"))
    
    def display_config(self):
        """
        Affiche la configuration système.
        """
        print("\n" + "=" * 60)
        print("CONFIGURATION SYSTÈME")
        print("=" * 60)
        
        print("🔧 MODE DE FONCTIONNEMENT:")
        print(f"  Debug: {'✅ Activé' if self.DEBUG_MODE else '❌ Désactivé'}")
        print(f"  Simulation: {'✅ Activé' if self.SIMULATION_MODE else '❌ Désactivé'}")
        
        print("\n⚡ PERFORMANCE:")
        print(f"  Signaux simultanés max: {self.MAX_CONCURRENT_SIGNALS}")
        print(f"  Délai traitement: {self.MESSAGE_PROCESSING_DELAY}s")
        
        print("\n🛡️ SÉCURITÉ:")
        print(f"  Vérifications risque: {'✅ Activées' if self.ENABLE_RISK_CHECKS else '❌ Désactivées'}")
        print(f"  Validation signaux: {'✅ Activée' if self.ENABLE_SIGNAL_VALIDATION else '❌ Désactivée'}")
        
        print("\n💾 HISTORIQUE:")
        print(f"  Sauvegarde: {'✅ Activée' if self.SAVE_SIGNALS_HISTORY else '❌ Désactivée'}")
        if self.SAVE_SIGNALS_HISTORY:
            print(f"  Fichier: {self.HISTORY_FILE_PATH}")
            print(f"  Entrées max: {self.MAX_HISTORY_ENTRIES}")
        
        print("=" * 60 + "\n")


# Instances globales de configuration
telegram_config = TelegramConfig()
trading_config = TradingConfig()
system_config = SystemConfig()

# Exemple de fichier .env complet
ENV_EXAMPLE = """
# ================================
# CONFIGURATION TELEGRAM
# ================================
TELEGRAM_MAT_API_ID=YOUR_TELEGRAM_API_ID_HERE
TELEGRAM_MAT_API_HASH=YOUR_TELEGRAM_API_HASH_HERE
TELEGRAM_MAT_SESSION=MAT.session
TELEGRAM_CHANNEL_1_ID=-2125503665
TELEGRAM_CHANNEL_2_ID=-2259371711

# Configuration avancée Telegram
TELEGRAM_CONNECTION_RETRIES=3
TELEGRAM_FLOOD_SLEEP_THRESHOLD=60
TELEGRAM_TIMEOUT=30

# ================================
# CONFIGURATION TRADING
# ================================
TOTAL_RISK_EUR=300.0
MAX_RISK_PERCENTAGE=7.0

# ChatGPT
GPT_KEY=YOUR_OPENAI_API_KEY_HERE
GPT_MODEL=gpt-4-turbo
GPT_TIMEOUT=30

# ================================
# CONFIGURATION MT5
# ================================
MT5_DEMO_LOGIN=YOUR_MT5_LOGIN_HERE
MT5_DEMO_MDP=YOUR_MT5_PASSWORD_HERE
MT5_DEMO_SERVEUR=YOUR_MT5_SERVER_HERE

# Configuration avancée MT5
MT5_TIMEOUT=60000
MT5_DEVIATION=20
MT5_MAGIC_BASE=234000

# ================================
# CONFIGURATION ORDRES
# ================================
ORDER_RETRY_COUNT=3
ORDER_RETRY_DELAY=1.0

# ================================
# CONFIGURATION SYSTÈME
# ================================
DEBUG_MODE=false
SIMULATION_MODE=false
MAX_CONCURRENT_SIGNALS=5
MESSAGE_PROCESSING_DELAY=0.5

# Sécurité
ENABLE_RISK_CHECKS=true
ENABLE_SIGNAL_VALIDATION=true

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_FILE_PATH=trading_bot.log

# Historique
SAVE_SIGNALS_HISTORY=true
HISTORY_FILE_PATH=signals_history.json
MAX_HISTORY_ENTRIES=1000
"""

def display_all_configs():
    """
    Affiche toutes les configurations du système.
    """
    print("\n" + "=" * 80)
    print("CONFIGURATION COMPLÈTE DU SYSTÈME DE TRADING")
    print("=" * 80)
    
    telegram_config.display_config()
    trading_config.display_config()
    system_config.display_config()
    
    print("=" * 80)
    print("🚀 PRÊT POUR LE TRADING AUTOMATISÉ!")
    print("=" * 80 + "\n")

def validate_all_configs():
    """
    Valide toutes les configurations et retourne le statut.
    
    Returns:
        dict: Statut de validation pour chaque composant
    """
    return {
        'telegram': telegram_config.is_valid_config(),
        'mt5': trading_config.is_mt5_configured(),
        'gpt': trading_config.is_gpt_configured(),
        'all_valid': (
            telegram_config.is_valid_config() and 
            trading_config.is_mt5_configured() and 
            trading_config.is_gpt_configured()
        )
    }

if __name__ == "__main__":
    # Afficher toutes les configurations
    display_all_configs()
    
    # Valider les configurations
    validation = validate_all_configs()
    
    print("🔍 VALIDATION DES CONFIGURATIONS:")
    print(f"  Telegram: {'✅' if validation['telegram'] else '❌'}")
    print(f"  MT5: {'✅' if validation['mt5'] else '❌'}")
    print(f"  ChatGPT: {'✅' if validation['gpt'] else '❌'}")
    print(f"  Système complet: {'✅ PRÊT' if validation['all_valid'] else '❌ CONFIGURATION INCOMPLÈTE'}")
    
    if not validation['all_valid']:
        print("\n💡 Complétez votre fichier .env avec les valeurs manquantes.")
        print("📋 Exemple de fichier .env complet:")
        print(ENV_EXAMPLE)