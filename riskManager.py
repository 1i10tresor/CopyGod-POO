import math
import MetaTrader5 as mt5
from info import Infos

class RiskManager:
    def __init__(self, total_risk_eur, max_risk_percentage=7.0):
        """
        Initialise le gestionnaire de risque.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un signal (3 positions)
            max_risk_percentage (float): Pourcentage maximum du capital à risquer (défaut: 7%)
        """
        self.total_risk_eur = total_risk_eur
        self.risk_per_position = total_risk_eur / 3  # Risque par position individuelle
        self.max_risk_percentage = max_risk_percentage
    
    def can_open_position(self, order_sender):
        """
        Vérifie si de nouvelles positions peuvent être ouvertes.
        """
        try:
            account_info = order_sender.get_account_info()
            if not account_info:
                print("Impossible d'obtenir les informations du compte")
                return False
            
            balance = account_info['balance']
            equity = account_info['equity']
            
            # Calculer le risque actuel
            current_risk = balance - equity
            current_risk_percentage = (current_risk / balance) * 100 if balance > 0 else 0
            
            print(f"Balance: {balance} {account_info['currency']}")
            print(f"Equity: {equity} {account_info['currency']}")
            print(f"Risque actuel: {current_risk:.2f} {account_info['currency']} ({current_risk_percentage:.2f}%)")
            print(f"Limite de risque: {self.max_risk_percentage}%")
            
            if current_risk_percentage >= self.max_risk_percentage:
                print(f"⚠️  RISQUE TROP ÉLEVÉ: {current_risk_percentage:.2f}% >= {self.max_risk_percentage}%")
                return False
            
            remaining_risk_percentage = self.max_risk_percentage - current_risk_percentage
            remaining_risk_eur = (remaining_risk_percentage / 100) * balance
            
            print(f"✅ Risque disponible: {remaining_risk_percentage:.2f}% ({remaining_risk_eur:.2f} {account_info['currency']})")
            
            # Vérifier si le risque total du signal est acceptable
            if self.total_risk_eur > remaining_risk_eur:
                print(f"⚠️  Risque du signal ({self.total_risk_eur:.2f}) > Risque disponible ({remaining_risk_eur:.2f})")
                return False
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la vérification du risque: {e}")
            return False
    
    def calculate_lot_size_for_signal(self, signals, channel_id=1):
        """
        Calcule les tailles de lot pour un signal complet.
        
        Args:
            signals: Signal(s) à traiter
            channel_id (int): ID du canal
        
        Returns:
            list: Liste des tailles de lot pour chaque ordre
        """
        if channel_id == 1:
            return self._calculate_lot_size_channel_1(signals)
        elif channel_id == 2:
            return self._calculate_lot_size_channel_2(signals)
        else:
            print(f"Canal {channel_id} non supporté")
            return []
    
    def _calculate_lot_size_channel_1(self, signal):
        """
        Calcule les tailles de lot pour le canal 1 (3 ordres avec TPs différents).
        """
        try:
            symbol = signal['symbol']
            entry_price = signal['entry_price']
            sl_price = signal['sl']
            tps = signal['tps']
            
            # Obtenir les informations du symbole via MT5
            symbol_info = Infos.get_symbol_info(symbol)
            if not symbol_info:
                print(f"Impossible d'obtenir les informations pour {symbol}")
                return [0.01, 0.01, 0.01]
            
            # Calculer la distance SL en points
            sl_distance_points = Infos.calculate_points_distance(symbol, entry_price, sl_price)
            
            if sl_distance_points <= 0:
                print("Distance SL invalide")
                return [0.01, 0.01, 0.01]
            
            # Obtenir la valeur du pip en EUR
            pip_value_eur = Infos.get_pip_value_eur(symbol, 1.0)
            if not pip_value_eur:
                print("Impossible de calculer la valeur du pip")
                return [0.01, 0.01, 0.01]
            
            # Calculer la taille de lot pour chaque TP
            lot_sizes = []
            
            for i in range(3):
                # Chaque position risque 1/3 du risque total
                position_risk = self.risk_per_position
                
                # Calculer la taille de lot
                # Risque = Lot_size × Distance_SL_points × Pip_value_EUR
                lot_size = position_risk / (sl_distance_points * pip_value_eur)
                
                # Arrondir vers le bas selon le step du lot
                lot_step = symbol_info['lot_step']
                lot_size = math.floor(lot_size / lot_step) * lot_step
                
                # Respecter les limites min/max
                min_lot = symbol_info['min_lot']
                max_lot = symbol_info['max_lot']
                lot_size = max(min_lot, min(lot_size, max_lot))
                
                lot_sizes.append(lot_size)
            
            print(f"Tailles de lot calculées pour {symbol}: {lot_sizes}")
            return lot_sizes
            
        except Exception as e:
            print(f"Erreur lors du calcul des lots pour le canal 1: {e}")
            return [0.01, 0.01, 0.01]
    
    def _calculate_lot_size_channel_2(self, signals):
        """
        Calcule les tailles de lot pour le canal 2 (3 ordres avec entrées différentes).
        """
        try:
            lot_sizes = []
            
            for signal in signals:
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
            
            print(f"Tailles de lot calculées pour le canal 2: {lot_sizes}")
            return lot_sizes
            
        except Exception as e:
            print(f"Erreur lors du calcul des lots pour le canal 2: {e}")
            return [0.01] * len(signals)
    
    def get_risk_statistics(self, order_sender):
        """
        Retourne des statistiques détaillées sur le risque du compte.
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
                'can_open_position': remaining_risk_percentage > 0 and self.total_risk_eur <= remaining_risk_eur,
                'currency': account_info['currency']
            }
            
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques de risque: {e}")
            return None
    
    def display_risk_status(self, order_sender):
        """
        Affiche le statut du risque de manière formatée.
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
        print(f"Risque par signal: {self.total_risk_eur:.2f} {stats['currency']}")
        print(f"Risque par position: {self.risk_per_position:.2f} {stats['currency']}")
        print("-" * 60)
        
        if stats['can_open_position']:
            print("✅ STATUT: Nouveaux signaux autorisés")
        else:
            print("🚫 STATUT: Nouveaux signaux BLOQUÉS")
        
        print("=" * 60 + "\n")