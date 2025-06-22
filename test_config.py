"""
Script de test de la configuration.
Vérifie que tous les paramètres nécessaires sont configurés.
"""

import os
from dotenv import load_dotenv

def test_configuration():
    """Teste la configuration du système."""
    print("🔧 TEST DE CONFIGURATION")
    print("=" * 50)
    
    # Charger le .env
    if not os.path.exists('.env'):
        print("❌ Fichier .env manquant!")
        print("💡 Créez le fichier .env avec vos clés")
        return False
    
    load_dotenv()
    
    errors = []
    warnings = []
    
    # Test Telegram DID
    print("\n📱 Configuration Telegram DID:")
    did_api_id = os.getenv("TELEGRAM_DID_API_ID", "0")
    did_api_hash = os.getenv("TELEGRAM_DID_API_HASH", "")
    
    if did_api_id == "0" or not did_api_id:
        errors.append("TELEGRAM_DID_API_ID non configuré")
    else:
        print(f"✅ DID API_ID: {did_api_id}")
    
    if not did_api_hash:
        errors.append("TELEGRAM_DID_API_HASH non configuré")
    else:
        print(f"✅ DID API_HASH: {did_api_hash[:8]}...")
    
    # Test OpenAI
    print("\n🤖 Configuration OpenAI:")
    gpt_key = os.getenv("GPT_KEY", "")
    
    if not gpt_key:
        errors.append("GPT_KEY non configuré")
    elif not gpt_key.startswith("sk-"):
        errors.append("GPT_KEY semble invalide (doit commencer par 'sk-')")
    else:
        print(f"✅ GPT_KEY: {gpt_key[:20]}...")
    
    # Test MT5 Accounts - Seulement DID et DEMO
    print("\n📈 Configuration MT5:")
    accounts = [
        ('DID', 'MT5_DID_LOGIN', 'MT5_DID_MDP', 'MT5_DID_SERVEUR'),
        ('DEMO', 'MT5_DEMO_LOGIN', 'MT5_DEMO_MDP', 'MT5_DEMO_SERVEUR')
    ]
    
    for account_name, login_key, password_key, server_key in accounts:
        login = os.getenv(login_key, "")
        password = os.getenv(password_key, "")
        server = os.getenv(server_key, "")
        
        print(f"\n📊 Compte {account_name}:")
        
        if not login:
            warnings.append(f"{login_key} non configuré")
            print(f"⚠️ Login: Non configuré")
        else:
            print(f"✅ Login: {login}")
        
        if not password:
            warnings.append(f"{password_key} non configuré")
            print(f"⚠️ Password: Non configuré")
        else:
            print(f"✅ Password: {'*' * len(password)}")
        
        if not server:
            warnings.append(f"{server_key} non configuré")
            print(f"⚠️ Server: Non configuré")
        else:
            print(f"✅ Server: {server}")
    
    # Test des canaux
    print("\n📺 Configuration Canaux:")
    channel1 = os.getenv("TELEGRAM_CHANNEL_1_ID", "")
    channel2 = os.getenv("TELEGRAM_CHANNEL_2_ID", "")
    
    if channel1:
        print(f"✅ Canal 1: {channel1}")
    else:
        warnings.append("TELEGRAM_CHANNEL_1_ID non configuré")
    
    if channel2:
        print(f"✅ Canal 2: {channel2}")
    else:
        warnings.append("TELEGRAM_CHANNEL_2_ID non configuré")
    
    # Test compte actif
    print("\n⚙️ Configuration Active:")
    telegram_active = os.getenv("TELEGRAM_ACTIVE_ACCOUNT", "DID")
    mt5_active = os.getenv("MT5_ACTIVE_ACCOUNT", "DEMO")
    
    print(f"📱 Telegram actif: {telegram_active}")
    print(f"📈 MT5 actif: {mt5_active}")
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ:")
    
    if errors:
        print(f"❌ {len(errors)} erreur(s) critique(s):")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print(f"⚠️ {len(warnings)} avertissement(s):")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors and not warnings:
        print("✅ Configuration complète!")
        return True
    elif not errors:
        print("✅ Configuration minimale OK")
        print("💡 Au moins un compte Telegram et un compte MT5 sont requis")
        return True
    else:
        print("❌ Configuration incomplète - Erreurs critiques à corriger")
        return False

if __name__ == "__main__":
    success = test_configuration()
    if success:
        print("\n🚀 Vous pouvez lancer le système avec:")
        print("   python launch_telegram_bot.py")
    else:
        print("\n🔧 Corrigez d'abord les erreurs dans le fichier .env")
        print("\n💡 Vérifiez que votre fichier .env contient:")
        print("   - TELEGRAM_DID_API_ID=26513066")
        print("   - TELEGRAM_DID_API_HASH=6c3198f742f9f01de443990154353d95")
        print("   - MT5_DEMO_LOGIN=166552")
        print("   - MT5_DEMO_MDP=g:y2c4Ju89")
        print("   - MT5_DEMO_SERVEUR=FusionMarkets-Demo")
        print("   - GPT_KEY=sk-proj-...")