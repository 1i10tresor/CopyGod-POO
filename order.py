import MetaTrader5 as mt5
from datetime import datetime
import time
from config import config

class SendOrder:
    def __init__(self):
        self.is_connected = False
        self.expected_demo_login = None
        self._initialize_mt5()
    
    def _initialize_mt5(self):
        """Initialise la connexion MT5 au compte démo."""
        try:
            print("🔄 Connexion à MT5...")
            
            if not mt5.initialize():
                print(f"❌ Erreur d'initialisation MT5: {mt5.last_error()}")
                return False
            
            if not all([config.MT5_LOGIN, config.MT5_PASSWORD, config.MT5_SERVER]):
                print("❌ Identifiants MT5 manquants")
                mt5.shutdown()
                return False
            
            self.expected_demo_login = int(config.MT5_LOGIN)
            
            # Se connecter
            authorized = mt5.login(
                login=self.expected_demo_login,
                password=config.MT5_PASSWORD,
                server=config.MT5_SERVER
            )
            
            if not authorized:
                print(f"❌ Échec connexion MT5: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            # Vérifier que c'est un compte démo
            if not self._verify_demo_account():
                mt5.shutdown()
                return False
            
            self.is_connected = True
            print("✅ Connexion MT5 établie (compte démo)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation MT5: {e}")
            return False
    
    def _verify_demo_account(self):
        """Vérifie que nous sommes sur un compte démo."""
        try:
            account_info = mt5.account_info()
            if not account_info:
                print("❌ Impossible d'obtenir les infos du compte")
                return False
            
            if account_info.login != self.expected_demo_login:
                print(f"❌ Mauvais compte: {account_info.login} != {self.expected_demo_login}")
                return False
            
            if account_info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
                print("🚨 ATTENTION: Ce n'est pas un compte démo!")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification compte: {e}")
            return False
    
    def get_account_info(self):
        """Retourne les informations du compte."""
        if not self._verify_demo_account():
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
                    'is_demo': account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO
                }
            return None
        except Exception as e:
            print(f"❌ Erreur récupération infos compte: {e}")
            return None
    
    def place_orders(self, signals, lot_sizes):
        """Place 3 ordres individuels."""
        if not self._verify_demo_account():
            print("🚫 Placement annulé - Compte démo non confirmé")
            return []
        
        results = []
        
        for i, (signal, lot_size) in enumerate(zip(signals, lot_sizes)):
            print(f"\n📈 Placement ordre {i+1}/3...")
            result = self._place_single_order(signal, lot_size, i+1)
            if result:
                results.append(result)
            time.sleep(0.1)  # Pause entre ordres
        
        print(f"✅ {len(results)}/3 ordres placés avec succès")
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
                "comment": f"Signal-{order_number}-DEMO",
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
            print("🔴 Connexion MT5 fermée")