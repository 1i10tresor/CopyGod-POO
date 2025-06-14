from datetime import datetime

class SendOrder:
    def __init__(self):
        """
        Initialise la classe SendOrder pour la gestion des ordres.
        """
        self.orders_history = []
    
    def place_order(self, signal, lot_size):
        """
        Place un ordre basé sur le signal et la taille de lot calculée.
        
        Args:
            signal (dict): Signal de trading validé
            lot_size (float): Nombre de lots calculé par RiskManager
        
        Returns:
            dict: Détails de l'ordre placé
        """
        try:
            order_details = {
                'timestamp': datetime.now().isoformat(),
                'symbol': signal['symbol'],
                'type': signal['sens'],
                'entry_price': signal['entry_price'],
                'lot_size': lot_size,
                'stop_loss': signal['sl'],
                'take_profits': signal['tps'],
                'status': 'PENDING'
            }
            
            # Ajouter à l'historique
            self.orders_history.append(order_details)
            
            # Afficher les détails de l'ordre (simulation)
            self._display_order(order_details)
            
            # TODO: Intégrer avec l'API de trading réelle
            # self._send_to_broker(order_details)
            
            return order_details
            
        except Exception as e:
            print(f"Erreur lors de la création de l'ordre: {e}")
            return None
    
    def _display_order(self, order_details):
        """
        Affiche les détails de l'ordre (simulation).
        
        Args:
            order_details (dict): Détails de l'ordre
        """
        print("=" * 50)
        print("NOUVEL ORDRE PLACÉ")
        print("=" * 50)
        print(f"Timestamp: {order_details['timestamp']}")
        print(f"Symbole: {order_details['symbol']}")
        print(f"Type: {order_details['type']}")
        print(f"Prix d'entrée: {order_details['entry_price']}")
        print(f"Taille de lot: {order_details['lot_size']}")
        print(f"Stop Loss: {order_details['stop_loss']}")
        print(f"Take Profits: {', '.join(map(str, order_details['take_profits']))}")
        print(f"Statut: {order_details['status']}")
        print("=" * 50)
    
    def get_orders_history(self):
        """
        Retourne l'historique des ordres.
        
        Returns:
            list: Liste des ordres placés
        """
        return self.orders_history
    
    def get_pending_orders(self):
        """
        Retourne les ordres en attente.
        
        Returns:
            list: Liste des ordres avec statut PENDING
        """
        return [order for order in self.orders_history if order['status'] == 'PENDING']
    
    def update_order_status(self, order_index, new_status):
        """
        Met à jour le statut d'un ordre.
        
        Args:
            order_index (int): Index de l'ordre dans l'historique
            new_status (str): Nouveau statut (FILLED, CANCELLED, etc.)
        
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            if 0 <= order_index < len(self.orders_history):
                self.orders_history[order_index]['status'] = new_status
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut: {e}")
            return False