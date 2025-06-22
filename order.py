import MetaTrader5 as mt5
from datetime import datetime
import time
from config import config

class SendOrder:
    def __init__(self, account_type='DEMO'):
        self.account_type = account_type.upper()
        self.is_connected = False
        self.current_login = None
        print(f"🔧 DEBUG: Initialisation SendOrder pour compte {self.account_type}")
        print(f"🔧 DEBUG: Type de self.account_type: {type(self.account_type)}")
        print(f"🔧 DEBUG: Valeur de self.account_type: '{self.account_type}'")
        self._initialize_mt5()
    
    def _initialize_mt5(self):
        """Initialise la connexion MT5 au compte spécifié."""
        try:
            print(f"🔄 Connexion à MT5 ({self.account_type})...")
            
            # DEBUG: Vérifier l'initialisation MT5
            print("🔧 DEBUG: Tentative d'initialisation MT5...")
            if not mt5.initialize():
                error = mt5.last_error()
                print(f"❌ Erreur d'initialisation MT5: {error}")
                print(f"🔧 DEBUG: Code erreur MT5: {error}")
                return False
            
            print("✅ DEBUG: MT5 initialisé avec succès")
            
            # DEBUG: Obtenir les identifiants
            print(f"🔧 DEBUG: Récupération des identifiants pour {self.account_type}...")
            print(f"🔧 DEBUG: Appel de config.get_mt5_credentials('{self.account_type}')")
            
            # Vérifier que config existe et a la méthode
            print(f"🔧 DEBUG: Type de config: {type(config)}")
            print(f"🔧 DEBUG: Attributs de config: {dir(config)}")
            
            credentials = config.get_mt5_credentials(self.account_type)
            print(f"🔧 DEBUG: Credentials reçus: {credentials}")
            print(f"🔧 DEBUG: Type de credentials: {type(credentials)}")
            
            if not credentials['login']:
                print(f"❌ DEBUG: Login manquant pour {self.account_type}")
                print(f"🔧 DEBUG: Login value: '{credentials['login']}'")
                mt5.shutdown()
                return False
                
            if not credentials['password']:
                print(f"❌ DEBUG: Password manquant pour {self.account_type}")
                print(f"🔧 DEBUG: Password value: '{credentials['password']}'")
                mt5.shutdown()
                return False
                
            if not credentials['server']:
                print(f"❌ DEBUG: Server manquant pour {self.account_type}")
                print(f"🔧 DEBUG: Server value: '{credentials['server']}'")
                mt5.shutdown()
                return False
            
            print(f"✅ DEBUG: Tous les identifiants présents")
            print(f"🔧 DEBUG: Login: {credentials['login']}")
            print(f"🔧 DEBUG: Server: {credentials['server']}")
            print(f"🔧 DEBUG: Password: {'*' * len(str(credentials['password']))}")
            
            self.current_login = credentials['login']
            
            # DEBUG: Tentative de connexion
            print(f"🔧 DEBUG: Tentative de connexion MT5...")
            print(f"🔧 DEBUG: mt5.login(login={credentials['login']}, password=***, server={credentials['server']})")
            
            authorized = mt5.login(
                login=credentials['login'],
                password=credentials['password'],
                server=credentials['server']
            )
            
            print(f"🔧 DEBUG: Résultat mt5.login(): {authorized}")
            
            if not authorized:
                error = mt5.last_error()
                print(f"❌ Échec connexion MT5 ({self.account_type}): {error}")
                print(f"🔧 DEBUG: Code erreur connexion: {error}")
                print(f"🔧 DEBUG: Détails erreur: {error}")
                mt5.shutdown()
                return False
            
            print(f"✅ DEBUG: Connexion MT5 réussie")
            
            # Vérifier la connexion
            print(f"🔧 DEBUG: Vérification du compte...")
            if not self._verify_account():
                print(f"❌ DEBUG: Échec vérification compte")
                mt5.shutdown()
                return False
            
            self.is_connected = True
            print(f"✅ Connexion MT5 établie sur le compte {self.account_type} (Login: {self.current_login})")
            return True
            
        except AttributeError as e:
            print(f"❌ Erreur d'attribut lors de l'initialisation MT5: {e}")
            print(f"🔧 DEBUG: AttributeError détaillée: {type(e).__name__}: {str(e)}")
            print(f"🔧 DEBUG: L'erreur concerne probablement un attribut manquant dans la classe Config")
            import traceback
            print(f"🔧 DEBUG: Traceback AttributeError: {traceback.format_exc()}")
            return False
        except Exception as e:
            print(f"❌ Erreur initialisation MT5: {e}")
            print(f"🔧 DEBUG: Exception générale détaillée: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"🔧 DEBUG: Traceback général: {traceback.format_exc()}")
            return False
    
    def _verify_account(self):
        """Vérifie que nous sommes connectés au bon compte."""
        try:
            print(f"🔧 DEBUG: Récupération des infos du compte...")
            account_info = mt5.account_info()
            
            if not account_info:
                error = mt5.last_error()
                print("❌ Impossible d'obtenir les infos du compte")
                print(f"🔧 DEBUG: Erreur account_info: {error}")
                return False
            
            print(f"🔧 DEBUG: Account info reçu: Login={account_info.login}, Expected={self.current_login}")
            
            if account_info.login != self.current_login:
                print(f"❌ Mauvais compte connecté: {account_info.login} != {self.current_login}")
                return False
            
            # Afficher le type de compte
            account_type_str = "DÉMO" if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else "RÉEL"
            print(f"📊 Compte {account_type_str} - Balance: {account_info.balance} {account_info.currency}")
            print(f"🔧 DEBUG: Trade mode: {account_info.trade_mode}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification compte: {e}")
            print(f"🔧 DEBUG: Exception vérification: {type(e).__name__}: {str(e)}")
            return False
    
    def get_account_info(self):
        """Retourne les informations du compte."""
        if not self._verify_account():
            return None
        
        try:
            account_info = mt5.account_info()
            if account_info:
                return {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'free_margin': account_info.margin_free,
                    'currency': account_info.currency,
                    'is_demo': account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO,
                    'account_type': self.account_type
                }
            return None
        except Exception as e:
            print(f"❌ Erreur récupération infos compte: {e}")
            return None
    
    def place_orders(self, signals, lot_sizes):
        """Place 3 ordres individuels."""
        if not self._verify_account():
            print(f"🚫 Placement annulé - Compte {self.account_type} non confirmé")
            return []
        
        results = []
        
        for i, (signal, lot_size) in enumerate(zip(signals, lot_sizes)):
            print(f"\n📈 Placement ordre {i+1}/3 sur {self.account_type}...")
            result = self._place_single_order(signal, lot_size, i+1)
            if result:
                results.append(result)
            time.sleep(0.1)  # Pause entre ordres
        
        print(f"✅ {len(results)}/3 ordres placés avec succès sur {self.account_type}")
        return results
    
    def _place_single_order(self, signal, lot_size, order_number):
        """Place un seul ordre."""
        try:
            symbol = signal['symbol']
            sens = signal['sens']
            entry_price = signal['entry_price']
            sl_price = signal['sl']
            tp_price = signal['tp']
            
            # Sélectionner le symbole
            if not mt5.symbol_select(symbol, True):
                print(f"❌ Impossible de sélectionner {symbol}")
                return None
            
            # Obtenir les infos du symbole
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                print(f"❌ Infos symbole {symbol} indisponibles")
                return None
            
            # Obtenir le prix actuel
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                print(f"❌ Prix actuel {symbol} indisponible")
                return None
            
            current_price = tick.ask if sens == 'BUY' else tick.bid
            
            # Déterminer le type d'ordre
            if abs(entry_price - current_price) <= 5 * symbol_info.point:
                # Ordre au marché
                order_type = mt5.ORDER_TYPE_BUY if sens == 'BUY' else mt5.ORDER_TYPE_SELL
                action = mt5.TRADE_ACTION_DEAL
                price = current_price
            else:
                # Ordre en attente
                if sens == 'BUY':
                    order_type = mt5.ORDER_TYPE_BUY_LIMIT if entry_price < current_price else mt5.ORDER_TYPE_BUY_STOP
                else:
                    order_type = mt5.ORDER_TYPE_SELL_LIMIT if entry_price > current_price else mt5.ORDER_TYPE_SELL_STOP
                action = mt5.TRADE_ACTION_PENDING
                price = entry_price
            
            # Normaliser les prix
            digits = symbol_info.digits
            price = round(price, digits)
            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)
            
            # Préparer la requête
            request = {
                "action": action,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 234000 + order_number,
                "comment": f"Signal-{order_number}-{self.account_type}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            print(f"📋 {sens} {symbol}: {lot_size} lots à {price} (SL: {sl_price}, TP: {tp_price})")
            
            # Envoyer l'ordre
            result = mt5.order_send(request)
            
            if result is None:
                error = mt5.last_error()
                print(f"❌ Ordre {order_number} - Erreur: {error}")
                return None
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"❌ Ordre {order_number} - Retcode: {result.retcode} - {result.comment}")
                return None
            
            print(f"✅ Ordre {order_number} placé - ID: {result.order}")
            
            return {
                'order_number': order_number,
                'symbol': symbol,
                'type': sens,
                'volume': lot_size,
                'price': price,
                'sl': sl_price,
                'tp': tp_price,
                'mt5_order_id': result.order,
                'account_type': self.account_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erreur placement ordre {order_number}: {e}")
            return None
    
    def close_connection(self):
        """Ferme la connexion MT5."""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            print(f"🔴 Connexion MT5 fermée ({self.account_type})")