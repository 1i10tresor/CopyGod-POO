"""
Script de lancement du système de trading Telegram.
"""

import asyncio
import sys
from telegramListener import main

def print_startup_info():
    """Affiche les informations de démarrage."""
    print("=" * 60)
    print("🤖 SYSTÈME DE TRADING TELEGRAM")
    print("=" * 60)
    print("✅ Connexion automatique Telegram")
    print("✅ Choix du compte MT5 (MAT/DID/DEMO)")
    print("✅ Surveillance 2 canaux Telegram")
    print("✅ Gestion risque personnalisée")
    print("✅ 3 ordres par signal")
    print("✅ Arrondi à l'inférieur")
    print("=" * 60)
    print()

def check_requirements():
    """Vérifie les dépendances."""
    try:
        import telethon
        import MetaTrader5
        import openai
        import dotenv
        print("✅ Toutes les dépendances installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

async def launch_system():
    """Lance le système de trading."""
    print_startup_info()
    
    if not check_requirements():
        return
    
    print("🚀 Lancement du système...")
    print("⚠️ Vous allez choisir le compte MT5 pour les ordres")
    print()
    
    response = input("Continuer ? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Lancement annulé")
        return
    
    print("\n🔄 Démarrage...")
    await main()

if __name__ == "__main__":
    try:
        asyncio.run(launch_system())
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt du système")
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)