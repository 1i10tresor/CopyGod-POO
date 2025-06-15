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
            
            account_info = mt5.account_info()
            if account_info:
                print(f"Compte: {account_info.login}")
                print(f"Balance: {account_info.balance} {account_info.currency}")
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation MT5: {e}")
            return False
    
    def place_signal_orders(self, signals, lot_sizes, channel_id=1):
        """
        Place tous les ordres pour un signal complet.
        
        Args:
            signals: Signal(s) à traiter
            lot_sizes (list): Tailles de lot pour chaque ordre
            channel_id (int): ID du canal
        
        Returns:
            list: Liste des résultats d'ordres
        """
        if channel_id == 1:
            return self._place_channel_1_orders(signals, lot_sizes)
        elif channel_id == 2:
            return self._place_channel_2_orders(signals, lot_sizes)
        else:
            print(f"Canal {channel_id} non supporté")
            return []
    
    def _place_channel_1_orders(self, signal, lot_sizes):
        """
        Place 3 ordres pour le canal 1 (même entrée, 3 TPs différents).
        """
        if not self.is_connected:
            print("MT5 n'est pas connecté")
            return []
        
        results = []
        symbol = signal['symbol']
        entry_price = signal['entry_price']
        sl_price = signal['sl']
        tps = signal['tps']
        sens = signal['sens']
        
        try:
            # Vérifier le symbole
            if not mt5.symbol_select(symbol, True):
                print(f"Symbole {symbol} non disponible")
                return []
            
            # Placer un ordre pour chaque TP
            for i in range(3):
                if i >= len(lot_sizes) or i >= len(tps):
                    break
                
                lot_size = lot_sizes[i]
                tp_price = tps[i]
                
                # Déterminer le type d'ordre
                order_type = mt5.ORDER_TYPE_BUY if sens == 'BUY' else mt5.ORDER_TYPE_SELL
                
                # Prix d'entrée
                if entry_price:
                    price = entry_price
                    action = mt5.TRADE_ACTION_PENDING
                else:
                    tick = mt5.symbol_info_tick(symbol)
                    price = tick.ask if sens == 'BUY' else tick.bid
                    action = mt5.TRADE_ACTION_DEAL
                
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
                    "magic": 234000 + i,  # Magic number différent pour chaque ordre
                    "comment": f"Signal Canal 1 - TP{i+1}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                # Envoyer l'ordre
                result = mt5.order_send(request)
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Erreur ordre TP{i+1}: {result.retcode} - {result.comment}")
                    continue
                
                # Créer les détails de l'ordre
                order_details = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'type': sens,
                    'entry_price': price,
                    'lot_size': lot_size,
                    'stop_loss': sl_price,
                    'take_profit': tp_price,
                    'tp_number': i + 1,
                    'status': 'FILLED' if action == mt5.TRADE_ACTION_DEAL else 'PENDING',
                    'mt5_order_id': result.order,
                    'mt5_deal_id': result.deal if hasattr(result, 'deal') else None,
                    'channel_id': 1
                }
                
                results.append(order_details)
                self.orders_history.append(order_details)
                
                print(f"✅ Ordre TP{i+1} placé: {lot_size} lots à {tp_price}")
                time.sleep(0.1)  # Petite pause entre les ordres
            
            if results:
                self._display_signal_orders(results)
            
            return results
            
        except Exception as e:
            print(f"Erreur lors du placement des ordres canal 1: {e}")
            return []
    
    def _place_channel_2_orders(self, signals, lot_sizes):
        """
        Place 3 ordres pour le canal 2 (3 entrées différentes, RR fixe).
        """
        if not self.is_connected:
            print("MT5 n'est pas connecté")
            return []
        
        results = []
        
        try:
            for i, (signal, lot_size) in enumerate(zip(signals, lot_sizes)):
                symbol = signal['symbol']
                entry_price = signal['entry_price']
                sl_price = signal['sl']
                tp_price = signal['tps'][0]  # Un seul TP par ordre
                sens = signal['sens']
                rr_ratio = signal['rr_ratio']
                
                # Vérifier le symbole
                if not mt5.symbol_select(symbol, True):
                    print(f"Symbole {symbol} non disponible")
                    continue
                
                # Type d'ordre
                order_type = mt5.ORDER_TYPE_BUY if sens == 'BUY' else mt5.ORDER_TYPE_SELL
                
                # Prix d'entrée
                if entry_price:
                    price = entry_price
                    action = mt5.TRADE_ACTION_PENDING
                else:
                    tick = mt5.symbol_info_tick(symbol)
                    price = tick.ask if sens == 'BUY' else tick.bid
                    action = mt5.TRADE_ACTION_DEAL
                
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
                    "magic": 235000 + i,  # Magic number différent
                    "comment": f"Signal Canal 2 - RR{rr_ratio}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                # Envoyer l'ordre
                result = mt5.order_send(request)
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Erreur ordre RR{rr_ratio}: {result.retcode} - {result.comment}")
                    continue
                
                # Créer les détails de l'ordre
                order_details = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'type': sens,
                    'entry_price': price,
                    'lot_size': lot_size,
                    'stop_loss': sl_price,
                    'take_profit': tp_price,
                    'rr_ratio': rr_ratio,
                    'order_index': i + 1,
                    'status': 'FILLED' if action == mt5.TRADE_ACTION_DEAL else 'PENDING',
                    'mt5_order_id': result.order,
                    'mt5_deal_id': result.deal if hasattr(result, 'deal') else None,
                    'channel_id': 2
                }
                
                results.append(order_details)
                self.orders_history.append(order_details)
                
                print(f"✅ Ordre RR{rr_ratio} placé: {lot_size} lots, entrée {entry_price}, TP {tp_price}")
                time.sleep(0.1)
            
            if results:
                self._display_signal_orders(results)
            
            return results
            
        except Exception as e:
            print(f"Erreur lors du placement des ordres canal 2: {e}")
            return []
    
    def _display_signal_orders(self, orders):
        """
        Affiche les détails des ordres d'un signal.
        """
        if not orders:
            return
        
        print("\n" + "=" * 70)
        print(f"SIGNAL TRAITÉ - CANAL {orders[0]['channel_id']} - {len(orders)} ORDRES PLACÉS")
        print("=" * 70)
        print(f"Symbole: {orders[0]['symbol']}")
        print(f"Direction: {orders[0]['type']}")
        print(f"Stop Loss: {orders[0]['stop_loss']}")
        print("-" * 70)
        
        for i, order in enumerate(orders, 1):
            if order['channel_id'] == 1:
                print(f"Ordre {i} - TP{order['tp_number']}: {order['lot_size']} lots → {order['take_profit']}")
            else:
                print(f"Ordre {i} - RR{order['rr_ratio']}: {order['lot_size']} lots → {order['take_profit']}")
            print(f"  ID MT5: {order['mt5_order_id']} | Statut: {order['status']}")
        
        print("=" * 70 + "\n")
    
    def get_account_info(self):
        """
        Retourne les informations du compte MT5.
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