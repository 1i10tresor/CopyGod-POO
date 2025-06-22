import MetaTrader5 as mt5
from datetime import datetime
import time
from config import config

class SendOrder:
    def __init__(self, account_type='DEMO'):
        """
        Initialise la connexion MT5 pour le compte spécifié.
        
        Args:
            account_type (str): Type de compte ('DID' ou 'DEMO')
        """
        self.account_type = account_type.upper()
        self.is_connected = False
        self.current_login = None
        
        print(f"🔧 Initialisation SendOrder pour compte {self.account_type}")
        
        # Vérifier que le type de compte est supporté
        if self.account_type not in ['DID', 'DEMO']:
            raise ValueError(f"Type de compte non supporté: {self.account_type}. Utilisez 'DID' ou 'DEMO'")
        
        # Initialiser la connexion MT5
        self._connect_to_mt5()
    
    def _connect_to_mt5(self):
        """Établit la connexion à MT5."""
        try:
            print(f"🔄 Connexion à MT5 ({self.account_type})...")
            
            # Initialiser MT5
            if not mt5.initialize():
                error = mt5.last_error()
                print(f"❌ Échec initialisation MT5: {error}")
                return
            
            # Récupérer les identifiants
            credentials = self._get_credentials()
            if not credentials:
                print(f"❌ Impossible de récupérer les identifiants pour {self.account_type}")
                mt5.shutdown()
                return
            
            # Se connecter au compte
            success = mt5.login(
                login=credentials['login'],
                password=credentials['password'],
                server=credentials['server']
            )
            
            if not success:
                error = mt5.last_error()
                print(f"❌ Échec connexion MT5: {error}")
                mt5.shutdown()
                return
            
            # Vérifier la connexion
            if self._verify_connection(credentials['login']):
                self.is_connected = True
                self.current_login = credentials['login']
                print(f"✅ Connexion MT5 établie sur {self.account_type}")
            else:
                print(f"❌ Vérification de connexion échouée")
                mt5.shutdown()
                
        except Exception as e:
            print(f"❌ Erreur lors de la connexion MT5: {e}")
            if mt5.initialize():
                mt5.shutdown()
    
    def _get_credentials(self):
        """Récupère les identifiants MT5 depuis la configuration."""
        try:
            return config.get_mt5_credentials(self.account_type)
        except Exception as e:
            print(f"❌ Erreur récupération identifiants: {e}")
            return None
    
    def _verify_connection(self, expected_login):
        """Vérifie que la connexion est établie sur le bon compte."""
        try:
            account_info = mt5.account_info()
            if not account_info:
                print("❌ Impossible de récupérer les infos du compte")
                return False
            
            if account_info.login != expected_login:
                print(f"❌ Connecté au mauvais compte: {account_info.login} != {expected_login}")
                return False
            
            # Afficher le type de compte
            account_type_str = "DÉMO" if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else "RÉEL"
            print(f"📊 Compte {account_type_str} - Balance: {account_info.balance} {account_info.currency}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification connexion: {e}")
            return False
    
    def get_account_info(self):
        """Retourne les informations du compte."""
        if not self.is_connected:
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
        """
        Place 3 ordres individuels sur MT5.
        
        Args:
            signals (list): Liste de 3 signaux
            lot_sizes (list): Liste de 3 tailles de lot
            
        Returns:
            list: Liste des résultats de placement
        """
        if not self.is_connected:
            print(f"🚫 Placement annulé - Compte {self.account_type} non connecté")
            return []
        
        if len(signals) != 3 or len(lot_sizes) != 3:
            print(f"❌ Erreur: Il faut exactement 3 signaux et 3 tailles de lot")
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
        """Place un seul ordre sur MT5."""
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