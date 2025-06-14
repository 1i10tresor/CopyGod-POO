# Exemple d'utilisation du système de trading

from signalPaser import SignalProcessor
from riskManager import RiskManager
from order import SendOrder
from info import Infos

class TradingBot:
    def __init__(self, total_risk_eur):
        """
        Initialise le bot de trading.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un groupe de 3 positions
        """
        self.risk_manager = RiskManager(total_risk_eur)
        self.order_sender = SendOrder()
        self.processed_signals = []
    
    def process_signal(self, signal_text):
        """
        Traite un signal de trading complet.
        
        Args:
            signal_text: Texte du signal à traiter
        
        Returns:
            dict: Résultat du traitement ou None si échec
        """
        # Créer un objet signal simulé
        class MockSignal:
            def __init__(self, text):
                self.text = text
        
        mock_signal = MockSignal(signal_text)
        
        # 1. Vérifier si c'est un signal valide
        processor = SignalProcessor(mock_signal)
        if not processor.is_signal():
            print("Le texte ne contient pas de signal de trading valide.")
            return None
        
        # 2. Extraire et valider le signal
        signal = processor.get_signal()
        if not signal:
            print("Impossible d'extraire ou de valider le signal.")
            return None
        
        print(f"Signal extrait: {signal}")
        
        # 3. Obtenir les informations de l'instrument
        symbol = signal['symbol']
        instrument_info = Infos.get_instrument_info(symbol)
        if not instrument_info:
            print(f"Instrument {symbol} non supporté.")
            return None
        
        # 4. Calculer la taille de lot
        pip_size = instrument_info['pip_size']
        pip_value = instrument_info['pip_value_per_lot_eur']
        lot_size = self.risk_manager.calculate_lot_size(signal, pip_size, pip_value)
        
        # 5. Valider la taille de lot
        min_lot, max_lot = Infos.get_lot_limits(symbol)
        lot_size = self.risk_manager.validate_lot_size(lot_size, min_lot, max_lot)
        
        print(f"Taille de lot calculée: {lot_size}")
        
        # 6. Placer l'ordre
        order_result = self.order_sender.place_order(signal, lot_size)
        
        if order_result:
            self.processed_signals.append({
                'signal': signal,
                'lot_size': lot_size,
                'order': order_result
            })
        
        return order_result

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le bot avec un risque total de 300 EUR pour 3 positions
    bot = TradingBot(total_risk_eur=300.0)
    
    # Exemple de signal de trading
    signal_text = """
    EURUSD SELL
    Entry: 1.0850
    SL: 1.0900
    TP1: 1.0800
    TP2: 1.0750
    """
    
    print("Traitement du signal de trading...")
    result = bot.process_signal(signal_text)
    
    if result:
        print("\nSignal traité avec succès!")
        print(f"Historique des ordres: {len(bot.order_sender.get_orders_history())} ordre(s)")
    else:
        print("\nÉchec du traitement du signal.")