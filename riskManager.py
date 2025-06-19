import math
import MetaTrader5 as mt5
from info import Infos
from config import config

class RiskManager:
    def __init__(self):
        self.total_risk_eur = config.TOTAL_RISK_EUR
        self.risk_per_position = self.total_risk_eur / 3
        self.max_risk_percentage = config.MAX_RISK_PERCENTAGE
    
    def can_open_position(self, account_info):
        """Vérifie si de nouvelles positions peuvent être ouvertes."""
        try:
            balance = account_info['balance']
            equity = account_info['equity']
            
            current_risk = balance - equity
            current_risk_percentage = (current_risk / balance) * 100 if balance > 0 else 0
            
            print(f"Risque actuel: {current_risk_percentage:.2f}% (limite: {self.max_risk_percentage}%)")
            
            return current_risk_percentage < self.max_risk_percentage
            
        except Exception as e:
            print(f"Erreur lors de la vérification du risque: {e}")
            return False
    
    def calculate_lot_sizes(self, signals):
        """Calcule les tailles de lot pour 3 signaux individuels."""
        lot_sizes = []
        
        for signal in signals:
            try:
                symbol = signal['symbol']
                entry_price = signal['entry_price']
                sl_price = signal['sl']
                
                # Obtenir les informations du symbole
                symbol_info = Infos.get_symbol_info(symbol)
                if not symbol_info:
                    lot_sizes.append(0.01)
                    continue
                
                # Calculer la distance SL
                sl_distance_points = Infos.calculate_points_distance(symbol, entry_price, sl_price)
                
                if sl_distance_points <= 0:
                    lot_sizes.append(0.01)
                    continue
                
                # Obtenir la valeur du pip
                pip_value_eur = Infos.get_pip_value_eur(symbol, 1.0)
                if not pip_value_eur:
                    lot_sizes.append(0.01)
                    continue
                
                # Calculer la taille de lot
                lot_size = self.risk_per_position / (sl_distance_points * pip_value_eur)
                
                # Arrondir et valider
                lot_step = symbol_info['lot_step']
                lot_size = math.floor(lot_size / lot_step) * lot_step
                lot_size = max(symbol_info['min_lot'], min(lot_size, symbol_info['max_lot']))
                
                lot_sizes.append(lot_size)
                
            except Exception as e:
                print(f"Erreur calcul lot pour signal {signal.get('order_index', '?')}: {e}")
                lot_sizes.append(0.01)
        
        print(f"Tailles de lot calculées: {lot_sizes}")
        return lot_sizes