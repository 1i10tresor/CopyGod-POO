"""
Script de lancement du système de trading Telegram.
Utilise ce script pour démarrer le bot en temps réel.
"""

import asyncio
import sys
from telegramListener import TradingSystemTelegram, main

def print_startup_info():
    """
    Affiche les informations de démarrage.
    """
    print("=" * 80)
    print("🤖 SYSTÈME DE TRADING TELEGRAM - TEMPS RÉEL")
    print("=" * 80)
    print("📋 Fonctionnalités:")
    print("  ✅ Écoute en temps réel des canaux Telegram")
    print("  ✅ Détection automatique des signaux")
    print("  ✅ Placement automatique des ordres MT5")
    print("  ✅ Gestion avancée des risques")
    print("  ✅ Support de 2 formats de canaux")
    print()
    print("🔧 Configuration requise:")
    print("  📁 Fichier .env avec vos identifiants")
    print("  📱 Accès aux canaux Telegram privés")
    print("  💹 Connexion MetaTrader 5 active")
    print("  🤖 Clé API OpenAI configurée")
    print()
    print("⚠️  IMPORTANT:")
    print("  - Le système va se connecter avec VOTRE compte Telegram")
    print("  - Assurez-vous d'avoir accès aux canaux surveillés")
    print("  - Vérifiez votre configuration MT5 avant de commencer")
    print("=" * 80)
    print()

def check_requirements():
    """
    Vérifie les prérequis avant le démarrage.
    """
    try:
        import telethon
        import MetaTrader5
        import openai
        import dotenv
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Exécutez: pip install -r requirements.txt")
        return False

async def launch_system():
    """
    Lance le système de trading Telegram.
    """
    print_startup_info()
    
    # Vérifier les prérequis
    if not check_requirements():
        return
    
    # Demander confirmation
    print("🚀 Prêt à démarrer le système de trading en temps réel.")
    print("⚠️  Le système va:")
    print("   1. Se connecter à votre compte Telegram")
    print("   2. Surveiller les canaux configurés")
    print("   3. Placer des ordres réels sur MT5")
    print()
    
    response = input("Continuer ? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Démarrage annulé par l'utilisateur")
        return
    
    print("\n🔄 Démarrage du système...")
    
    # Lancer le système principal
    await main()

if __name__ == "__main__":
    try:
        # Lancer avec asyncio
        asyncio.run(launch_system())
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du système demandé")
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)