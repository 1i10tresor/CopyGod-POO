import math
import MetaTrader5 as mt5
from info import Infos

class RiskManager:
    def __init__(self, risk_per_signal_eur):
        self.risk_per_signal_eur = risk_per_signal_eur
        self.risk_per_position = risk_per_signal_eur / 3  # Répartition égale sur 3 positions
        print(f"💰 Risque configuré: {risk_per_signal_eur}€ par signal ({self.risk_per_position:.2f}€ par position)")
    
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
                    print(f"❌ Infos symbole {symbol} indisponibles")
                    lot_sizes.append(0.01)
                    continue
                
                # Calculer la distance SL en points
                sl_distance_points = Infos.calculate_points_distance(symbol, entry_price, sl_price)
                
                if sl_distance_points <= 0:
                    print(f"❌ Distance SL invalide: {sl_distance_points}")
                    lot_sizes.append(0.01)
                    continue
                
                # Obtenir la valeur du pip en EUR
                pip_value_eur = Infos.get_pip_value_eur(symbol, 1.0)
                if not pip_value_eur or pip_value_eur <= 0:
                    print(f"❌ Valeur pip invalide pour {symbol}")
                    lot_sizes.append(0.01)
                    continue
                
                # Calculer la taille de lot théorique
                # Risque = Distance_SL * Pip_Value * Lot_Size
                # Donc: Lot_Size = Risque / (Distance_SL * Pip_Value)
                theoretical_lot_size = self.risk_per_position / (sl_distance_points * pip_value_eur)
                
                # Arrondir à l'inférieur selon le lot_step
                lot_step = symbol_info['lot_step']
                lot_size = math.floor(theoretical_lot_size / lot_step) * lot_step
                
                # Respecter les limites min/max
                min_lot = symbol_info['min_lot']
                max_lot = symbol_info['max_lot']
                lot_size = max(min_lot, min(lot_size, max_lot))
                
                # Vérifier que le risque réel ne dépasse pas le risque défini
                real_risk = sl_distance_points * pip_value_eur * lot_size
                if real_risk > self.risk_per_position:
                    # Réduire encore si nécessaire
                    lot_size = math.floor((self.risk_per_position / (sl_distance_points * pip_value_eur)) / lot_step) * lot_step
                    lot_size = max(min_lot, lot_size)
                    real_risk = sl_distance_points * pip_value_eur * lot_size
                
                lot_sizes.append(lot_size)
                print(f"📊 {symbol}: Lot {lot_size} → Risque réel {real_risk:.2f}€")
                
            except Exception as e:
                print(f"❌ Erreur calcul lot pour {signal.get('symbol', '?')}: {e}")
                lot_sizes.append(0.01)
        
        total_risk = sum([sl_distance_points * pip_value_eur * lot for lot in lot_sizes])
        print(f"💰 Risque total calculé: {total_risk:.2f}€ (limite: {self.risk_per_signal_eur}€)")
        
        return lot_sizes