"""
Script de lancement simplifié du système de trading Telegram.
"""

import asyncio
import sys
from telegramListener import main

def print_startup_info():
    """Affiche les informations de démarrage."""
    print("=" * 60)
    print("🤖 SYSTÈME DE TRADING TELEGRAM SIMPLIFIÉ")
    print("=" * 60)
    print("✅ Connexion automatique au compte Telegram")
    print("✅ Connexion forcée au compte MT5 démo")
    print("✅ Surveillance de 2 canaux Telegram")
    print("✅ Traitement automatique des signaux")
    print("✅ Placement automatique de 3 ordres par signal")
    print("✅ Système de retry intégré (3 tentatives)")
    print("=" * 60)
    print()

def check_requirements():
    """Vérifie les dépendances."""
    try:
        import telethon
        import MetaTrader5
        import openai
        import dotenv
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

async def launch_system():
    """Lance le système de trading."""
    print_startup_info()
    
    if not check_requirements():
        return
    
    print("🚀 Démarrage du système...")
    print("⚠️ Le système va placer des ordres réels sur MT5 (compte démo)")
    print()
    
    response = input("Continuer ? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Démarrage annulé")
        return
    
    print("\n🔄 Lancement...")
    await main()

if __name__ == "__main__":
    try:
        asyncio.run(launch_system())
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt du système")
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)