import MetaTrader5 as mt5
from datetime import datetime
import time

class SendOrder:
    def __init__(self):
        """
        Initialise la classe SendOrder pour la gestion des ordres MT5.
        """
        self.orders_history = []
        self.is_connected = False
        self._initialize_mt5()
    
    def _initialize_mt5(self):
        """
        Initialise la connexion à MetaTrader 5.
        """
        try:
            if not mt5.initialize():
                print(f"Erreur d'initialisation MT5: {mt5.last_error()}")
                return False
            
            self.is_connected = True
            print("Connexion MT5 établie avec succès")
            
            # Afficher les informations du compte
            account_info = mt5.account_info()
            if account_info:
                print(f"Compte: {account_info.login}")
                print(f"Balance: {account_info.balance} {account_info.currency}")
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation MT5: {e}")
            return False
    
    def place_order(self, signal, lot_size):
        """
        Place un ordre sur MT5 basé sur le signal et la taille de lot calculée.
        
        Args:
            signal (dict): Signal de trading validé
            lot_size (float): Nombre de lots calculé par RiskManager
        
        Returns:
            dict: Détails de l'ordre placé ou None si échec
        """
        if not self.is_connected:
            print("MT5 n'est pas connecté")
            return None
        
        try:
            symbol = signal['symbol']
            
            # Vérifier que le symbole existe
            if not mt5.symbol_select(symbol, True):
                print(f"Symbole {symbol} non disponible")
                return None
            
            # Obtenir les informations du symbole
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                print(f"Impossible d'obtenir les informations pour {symbol}")
                return None
            
            # Préparer la requête d'ordre
            order_type = mt5.ORDER_TYPE_BUY if signal['sens'] == 'BUY' else mt5.ORDER_TYPE_SELL
            
            # Prix d'entrée (utiliser le prix du marché si pas spécifié)
            if signal['entry_price']:
                price = signal['entry_price']
                action = mt5.TRADE_ACTION_PENDING
            else:
                price = mt5.symbol_info_tick(symbol).ask if signal['sens'] == 'BUY' else mt5.symbol_info_tick(symbol).bid
                action = mt5.TRADE_ACTION_DEAL
            
            # Préparer la requête
            request = {
                "action": action,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": signal['sl'],
                "tp": signal['tps'][0] if signal['tps'] else None,  # Premier TP seulement
                "deviation": 20,
                "magic": 234000,
                "comment": "Signal automatique",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Envoyer l'ordre
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Erreur lors de l'envoi de l'ordre: {result.retcode} - {result.comment}")
                return None
            
            # Créer les détails de l'ordre
            order_details = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'type': signal['sens'],
                'entry_price': price,
                'lot_size': lot_size,
                'stop_loss': signal['sl'],
                'take_profits': signal['tps'],
                'status': 'FILLED',
                'mt5_order_id': result.order,
                'mt5_deal_id': result.deal if hasattr(result, 'deal') else None
            }
            
            # Ajouter à l'historique
            self.orders_history.append(order_details)
            
            # Afficher les détails
            self._display_order(order_details)
            
            # Placer les TPs supplémentaires si nécessaire
            if len(signal['tps']) > 1:
                self._place_additional_tps(symbol, signal['tps'][1:], lot_size, signal['sens'])
            
            return order_details
            
        except Exception as e:
            print(f"Erreur lors de la création de l'ordre MT5: {e}")
            return None
    
    def _place_additional_tps(self, symbol, additional_tps, lot_size, direction):
        """
        Place des ordres TP supplémentaires.
        
        Args:
            symbol (str): Symbole de trading
            additional_tps (list): Liste des TPs supplémentaires
            lot_size (float): Taille de lot
            direction (str): Direction BUY ou SELL
        """
        try:
            for tp_price in additional_tps:
                order_type = mt5.ORDER_TYPE_SELL_LIMIT if direction == 'BUY' else mt5.ORDER_TYPE_BUY_LIMIT
                
                request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": symbol,
                    "volume": lot_size / len(additional_tps),  # Diviser le volume
                    "type": order_type,
                    "price": tp_price,
                    "deviation": 20,
                    "magic": 234000,
                    "comment": "TP supplémentaire",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"TP supplémentaire placé à {tp_price}")
                else:
                    print(f"Erreur TP supplémentaire: {result.comment}")
                    
        except Exception as e:
            print(f"Erreur lors du placement des TPs supplémentaires: {e}")
    
    def _display_order(self, order_details):
        """
        Affiche les détails de l'ordre.
        
        Args:
            order_details (dict): Détails de l'ordre
        """
        print("=" * 50)
        print("NOUVEL ORDRE PLACÉ SUR MT5")
        print("=" * 50)
        print(f"Timestamp: {order_details['timestamp']}")
        print(f"Symbole: {order_details['symbol']}")
        print(f"Type: {order_details['type']}")
        print(f"Prix d'entrée: {order_details['entry_price']}")
        print(f"Taille de lot: {order_details['lot_size']}")
        print(f"Stop Loss: {order_details['stop_loss']}")
        print(f"Take Profits: {', '.join(map(str, order_details['take_profits']))}")
        print(f"Statut: {order_details['status']}")
        if order_details.get('mt5_order_id'):
            print(f"ID Ordre MT5: {order_details['mt5_order_id']}")
        print("=" * 50)
    
    def get_account_info(self):
        """
        Retourne les informations du compte MT5.
        
        Returns:
            dict: Informations du compte ou None si erreur
        """
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
                    'currency': account_info.currency
                }
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération des informations du compte: {e}")
            return None
    
    def get_open_positions(self):
        """
        Retourne les positions ouvertes.
        
        Returns:
            list: Liste des positions ouvertes
        """
        if not self.is_connected:
            return []
        
        try:
            positions = mt5.positions_get()
            return list(positions) if positions else []
        except Exception as e:
            print(f"Erreur lors de la récupération des positions: {e}")
            return []
    
    def get_orders_history(self):
        """
        Retourne l'historique des ordres.
        
        Returns:
            list: Liste des ordres placés
        """
        return self.orders_history
    
    def close_connection(self):
        """
        Ferme la connexion MT5.
        """
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            print("Connexion MT5 fermée")