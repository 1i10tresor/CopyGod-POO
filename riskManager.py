import math

class RiskManager:
    def __init__(self, total_risk_eur):
        """
        Initialise le gestionnaire de risque.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un groupe de 3 positions
        """
        self.total_risk_eur = total_risk_eur
        self.risk_per_position = total_risk_eur / 3
    
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
    
    def validate_lot_size(self, lot_size, min_lot=0.01, max_lot=100):
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