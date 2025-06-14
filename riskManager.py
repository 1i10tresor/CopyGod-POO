import math
import MetaTrader5 as mt5

class RiskManager:
    def __init__(self, total_risk_eur, max_risk_percentage=7.0):
        """
        Initialise le gestionnaire de risque.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un groupe de 3 positions
            max_risk_percentage (float): Pourcentage maximum du capital à risquer (défaut: 7%)
        """
        self.total_risk_eur = total_risk_eur
        self.risk_per_position = total_risk_eur / 3
        self.max_risk_percentage = max_risk_percentage
    
    def can_open_position(self, order_sender):
        """
        Vérifie si une nouvelle position peut être ouverte en fonction du risque total.
        
        Args:
            order_sender: Instance de SendOrder pour accéder aux informations du compte
        
        Returns:
            bool: True si une position peut être ouverte, False sinon
        """
        try:
            # Obtenir les informations du compte
            account_info = order_sender.get_account_info()
            if not account_info:
                print("Impossible d'obtenir les informations du compte")
                return False
            
            balance = account_info['balance']
            equity = account_info['equity']
            
            # Calculer le risque actuel (différence entre balance et equity)
            current_risk = balance - equity
            current_risk_percentage = (current_risk / balance) * 100 if balance > 0 else 0
            
            print(f"Balance: {balance} {account_info['currency']}")
            print(f"Equity: {equity} {account_info['currency']}")
            print(f"Risque actuel: {current_risk:.2f} {account_info['currency']} ({current_risk_percentage:.2f}%)")
            print(f"Limite de risque: {self.max_risk_percentage}%")
            
            # Vérifier si le risque dépasse la limite
            if current_risk_percentage >= self.max_risk_percentage:
                print(f"⚠️  RISQUE TROP ÉLEVÉ: {current_risk_percentage:.2f}% >= {self.max_risk_percentage}%")
                print("Aucune nouvelle position ne sera ouverte")
                return False
            
            # Calculer le risque restant disponible
            remaining_risk_percentage = self.max_risk_percentage - current_risk_percentage
            remaining_risk_eur = (remaining_risk_percentage / 100) * balance
            
            print(f"✅ Risque disponible: {remaining_risk_percentage:.2f}% ({remaining_risk_eur:.2f} {account_info['currency']})")
            
            # Vérifier si le risque de la nouvelle position est acceptable
            if self.risk_per_position > remaining_risk_eur:
                print(f"⚠️  Risque de la position ({self.risk_per_position:.2f}) > Risque disponible ({remaining_risk_eur:.2f})")
                return False
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la vérification du risque: {e}")
            return False
    
    def calculate_lot_size(self, signal, pip_size, pip_value_per_lot_eur):
        """
        Calcule le nombre de lots pour une position en fonction du risque défini.
        
        Args:
            signal (dict): Signal de trading contenant entry_price et sl
            pip_size (float): Taille d'un pip pour l'instrument (ex: 0.0001 pour EURUSD)
            pip_value_per_lot_eur (float): Valeur d'un pip pour un lot standard en EUR
        
        Returns:
            float: Nombre de lots arrondi vers le bas
        """
        try:
            entry_price = signal['entry_price']
            sl_price = signal['sl']
            
            # Calculer la distance en pips entre entry et stop loss
            price_difference = abs(entry_price - sl_price)
            pips_distance = price_difference / pip_size
            
            # Calculer le nombre de lots
            # Risque = Nombre de lots × Distance en pips × Valeur par pip
            # Donc: Nombre de lots = Risque / (Distance en pips × Valeur par pip)
            lot_size = self.risk_per_position / (pips_distance * pip_value_per_lot_eur)
            
            # Arrondir vers le bas
            lot_size = math.floor(lot_size * 100) / 100  # Arrondi à 2 décimales vers le bas
            
            return max(lot_size, 0.01)  # Minimum 0.01 lot
            
        except Exception as e:
            print(f"Erreur lors du calcul de la taille de lot: {e}")
            return 0.01
    
    def get_risk_statistics(self, order_sender):
        """
        Retourne des statistiques détaillées sur le risque du compte.
        
        Args:
            order_sender: Instance de SendOrder
        
        Returns:
            dict: Statistiques de risque
        """
        try:
            account_info = order_sender.get_account_info()
            if not account_info:
                return None
            
            balance = account_info['balance']
            equity = account_info['equity']
            margin = account_info['margin']
            free_margin = account_info['free_margin']
            
            current_risk = balance - equity
            current_risk_percentage = (current_risk / balance) * 100 if balance > 0 else 0
            remaining_risk_percentage = max(0, self.max_risk_percentage - current_risk_percentage)
            remaining_risk_eur = (remaining_risk_percentage / 100) * balance
            
            # Obtenir le nombre de positions ouvertes
            positions = order_sender.get_open_positions()
            open_positions_count = len(positions)
            
            return {
                'balance': balance,
                'equity': equity,
                'margin_used': margin,
                'free_margin': free_margin,
                'current_risk_eur': current_risk,
                'current_risk_percentage': current_risk_percentage,
                'max_risk_percentage': self.max_risk_percentage,
                'remaining_risk_percentage': remaining_risk_percentage,
                'remaining_risk_eur': remaining_risk_eur,
                'open_positions_count': open_positions_count,
                'can_open_position': remaining_risk_percentage > 0 and self.risk_per_position <= remaining_risk_eur,
                'currency': account_info['currency']
            }
            
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques de risque: {e}")
            return None
    
    def display_risk_status(self, order_sender):
        """
        Affiche le statut du risque de manière formatée.
        
        Args:
            order_sender: Instance de SendOrder
        """
        stats = self.get_risk_statistics(order_sender)
        if not stats:
            print("Impossible d'afficher le statut du risque")
            return
        
        print("\n" + "=" * 60)
        print("STATUT DU RISQUE DU COMPTE")
        print("=" * 60)
        print(f"Balance: {stats['balance']:.2f} {stats['currency']}")
        print(f"Equity: {stats['equity']:.2f} {stats['currency']}")
        print(f"Marge utilisée: {stats['margin_used']:.2f} {stats['currency']}")
        print(f"Marge libre: {stats['free_margin']:.2f} {stats['currency']}")
        print(f"Positions ouvertes: {stats['open_positions_count']}")
        print("-" * 60)
        print(f"Risque actuel: {stats['current_risk_eur']:.2f} {stats['currency']} ({stats['current_risk_percentage']:.2f}%)")
        print(f"Limite de risque: {stats['max_risk_percentage']:.2f}%")
        print(f"Risque disponible: {stats['remaining_risk_eur']:.2f} {stats['currency']} ({stats['remaining_risk_percentage']:.2f}%)")
        print(f"Risque par position: {self.risk_per_position:.2f} {stats['currency']}")
        print("-" * 60)
        
        if stats['can_open_position']:
            print("✅ STATUT: Nouvelles positions autorisées")
        else:
            print("🚫 STATUT: Nouvelles positions BLOQUÉES")
        
        print("=" * 60 + "\n")
    
    def get_risk_per_position(self):
        """
        Retourne le risque par position.
        
        Returns:
            float: Risque par position en EUR
        """
        return self.risk_per_position
    
    def get_total_risk(self):
        """
        Retourne le risque total.
        
        Returns:
            float: Risque total en EUR
        """
        return self.total_risk_eur
    
    def validate_lot_size(self, lot_size, min_lot=0.01, max_lot=1):
        """
        Valide que la taille de lot est dans les limites acceptables.
        
        Args:
            lot_size (float): Taille de lot à valider
            min_lot (float): Taille minimale de lot
            max_lot (float): Taille maximale de lot
        
        Returns:
            float: Taille de lot validée
        """
        if lot_size < min_lot:
            return min_lot
        elif lot_size > max_lot:
            return max_lot
        return lot_size