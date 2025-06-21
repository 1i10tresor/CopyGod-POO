"""
Script de test de la configuration.
Vérifie que tous les paramètres nécessaires sont configurés.
"""

import os
from dotenv import load_dotenv

def test_configuration():
    """Teste la configuration du système."""
    print("🔧 TEST DE CONFIGURATION")
    print("=" * 40)
    
    # Charger le .env
    if not os.path.exists('.env'):
        print("❌ Fichier .env manquant!")
        print("💡 Copiez .env.example vers .env et remplissez les valeurs")
        return False
    
    load_dotenv()
    
    errors = []
    warnings = []
    
    # Test Telegram
    print("\n📱 Configuration Telegram:")
    api_id = os.getenv("TELEGRAM_API_ID", "0")
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    
    if api_id == "0" or api_id == "YOUR_API_ID_HERE":
        errors.append("TELEGRAM_API_ID non configuré")
    else:
        print(f"✅ API_ID: {api_id}")
    
    if not api_hash or api_hash == "YOUR_API_HASH_HERE":
        errors.append("TELEGRAM_API_HASH non configuré")
    else:
        print(f"✅ API_HASH: {api_hash[:8]}...")
    
    # Test OpenAI
    print("\n🤖 Configuration OpenAI:")
    gpt_key = os.getenv("GPT_KEY", "")
    
    if not gpt_key or gpt_key == "YOUR_OPENAI_API_KEY_HERE":
        errors.append("GPT_KEY non configuré")
    else:
        print(f"✅ GPT_KEY: {gpt_key[:12]}...")
    
    # Test MT5 Accounts
    print("\n📈 Configuration MT5:")
    accounts = ['MAT', 'DID', 'DEMO']
    
    for account in accounts:
        login = os.getenv(f"MT5_{account}_LOGIN", "")
        password = os.getenv(f"MT5_{account}_PASSWORD", "")
        server = os.getenv(f"MT5_{account}_SERVER", "")
        
        print(f"\n📊 Compte {account}:")
        
        if not login or login == f"YOUR_{account}_LOGIN":
            warnings.append(f"MT5_{account}_LOGIN non configuré")
            print(f"⚠️ Login: Non configuré")
        else:
            print(f"✅ Login: {login}")
        
        if not password or password == f"YOUR_{account}_PASSWORD":
            warnings.append(f"MT5_{account}_PASSWORD non configuré")
            print(f"⚠️ Password: Non configuré")
        else:
            print(f"✅ Password: {'*' * len(password)}")
        
        if not server or server == f"YOUR_{account}_SERVER":
            warnings.append(f"MT5_{account}_SERVER non configuré")
            print(f"⚠️ Server: Non configuré")
        else:
            print(f"✅ Server: {server}")
    
    # Résumé
    print("\n" + "=" * 40)
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
        print("✅ Configuration minimale OK (au moins un compte MT5 requis)")
        return True
    else:
        print("❌ Configuration incomplète")
        return False

if __name__ == "__main__":
    test_configuration()