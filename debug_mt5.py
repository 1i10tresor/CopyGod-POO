"""
Script de debug spécifique pour MT5.
Teste la connexion MT5 avec des logs détaillés.
"""

import os
import MetaTrader5 as mt5
from dotenv import load_dotenv
from config import config

def debug_mt5_connection():
    """Debug complet de la connexion MT5."""
    print("🔧 DEBUG MT5 - ANALYSE COMPLÈTE")
    print("=" * 50)
    
    # Charger le .env
    load_dotenv()
    
    # Test 1: Vérifier l'installation MT5
    print("\n1️⃣ Test d'installation MT5:")
    try:
        import MetaTrader5 as mt5
        print("✅ Module MetaTrader5 importé")
        print(f"🔧 Version MT5: {mt5.__version__ if hasattr(mt5, '__version__') else 'Inconnue'}")
    except ImportError as e:
        print(f"❌ Erreur import MT5: {e}")
        return False
    
    # Test 2: Initialisation MT5
    print("\n2️⃣ Test d'initialisation MT5:")
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"❌ Échec initialisation MT5: {error}")
        print("💡 Vérifiez que MetaTrader 5 est installé et fermé")
        return False
    else:
        print("✅ MT5 initialisé avec succès")
    
    # Test 3: Vérifier les variables d'environnement
    print("\n3️⃣ Test des variables d'environnement:")
    
    accounts = ['MAT', 'DID', 'DEMO']
    for account in accounts:
        print(f"\n📊 Compte {account}:")
        
        login_key = f"MT5_{account}_LOGIN"
        password_key = f"MT5_{account}_MDP"
        server_key = f"MT5_{account}_SERVEUR"
        
        login = os.getenv(login_key, "")
        password = os.getenv(password_key, "")
        server = os.getenv(server_key, "")
        
        print(f"   {login_key}: '{login}' {'✅' if login else '❌'}")
        print(f"   {password_key}: '{'*' * len(password) if password else ''}' {'✅' if password else '❌'}")
        print(f"   {server_key}: '{server}' {'✅' if server else '❌'}")
        
        if all([login, password, server]):
            print(f"   🔧 Test connexion {account}...")
            
            try:
                login_int = int(login)
                print(f"   🔧 Login converti: {login_int}")
                
                # Tentative de connexion
                print(f"   🔧 mt5.login({login_int}, ***, {server})")
                authorized = mt5.login(login=login_int, password=password, server=server)
                
                if authorized:
                    print(f"   ✅ Connexion {account} réussie!")
                    
                    # Vérifier les infos du compte
                    account_info = mt5.account_info()
                    if account_info:
                        account_type_str = "DÉMO" if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else "RÉEL"
                        print(f"   📊 Type: {account_type_str}")
                        print(f"   💰 Balance: {account_info.balance} {account_info.currency}")
                        print(f"   🏦 Serveur: {account_info.server}")
                    else:
                        print(f"   ⚠️ Impossible de récupérer les infos du compte")
                else:
                    error = mt5.last_error()
                    print(f"   ❌ Échec connexion {account}: {error}")
                    
            except ValueError:
                print(f"   ❌ Login invalide (doit être un nombre): '{login}'")
            except Exception as e:
                print(f"   ❌ Erreur connexion {account}: {e}")
        else:
            print(f"   ⚠️ Identifiants incomplets pour {account}")
    
    # Test 4: Test avec la classe Config
    print("\n4️⃣ Test avec la classe Config:")
    
    for account in accounts:
        print(f"\n📊 Test Config.get_mt5_credentials('{account}'):")
        try:
            credentials = config.get_mt5_credentials(account)
            print(f"   Résultat: {credentials}")
            
            if all([credentials['login'], credentials['password'], credentials['server']]):
                print(f"   ✅ Credentials complets")
            else:
                print(f"   ❌ Credentials incomplets")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Fermer MT5
    mt5.shutdown()
    print("\n🔴 MT5 fermé")
    
    print("\n" + "=" * 50)
    print("🏁 DEBUG TERMINÉ")
    
    return True

if __name__ == "__main__":
    debug_mt5_connection()