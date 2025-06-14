# Exemple d'utilisation du système de trading avec MT5

from signalPaser import SignalProcessor
from riskManager import RiskManager
from order import SendOrder
from info import Infos

class TradingBot:
    def __init__(self, total_risk_eur, max_risk_percentage=7.0):
        """
        Initialise le bot de trading.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un groupe de 3 positions
            max_risk_percentage (float): Pourcentage maximum du capital à risquer
        """
        self.risk_manager = RiskManager(total_risk_eur, max_risk_percentage)
        self.order_sender = SendOrder()
        self.processed_signals = []
    
    def process_signal(self, signal_text):
        """
        Traite un signal de trading complet avec vérification du risque.
        
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
        
        # 3. Vérifier le statut du risque AVANT de continuer
        print("\n🔍 Vérification du risque du compte...")
        self.risk_manager.display_risk_status(self.order_sender)
        
        if not self.risk_manager.can_open_position(self.order_sender):
            print("❌ Signal ignoré: Risque du compte trop élevé")
            return None
        
        # 4. Obtenir les informations de l'instrument
        symbol = signal['symbol']
        instrument_info = Infos.get_instrument_info(symbol)
        if not instrument_info:
            print(f"Instrument {symbol} non supporté.")
            return None
        
        # 5. Calculer la taille de lot
        pip_size = instrument_info['pip_size']
        pip_value = instrument_info['pip_value_per_lot_eur']
        lot_size = self.risk_manager.calculate_lot_size(signal, pip_size, pip_value)
        
        # 6. Valider la taille de lot
        min_lot, max_lot = Infos.get_lot_limits(symbol)
        lot_size = self.risk_manager.validate_lot_size(lot_size, min_lot, max_lot)
        
        print(f"Taille de lot calculée: {lot_size}")
        
        # 7. Placer l'ordre sur MT5
        print("\n📈 Placement de l'ordre sur MT5...")
        order_result = self.order_sender.place_order(signal, lot_size)
        
        if order_result:
            self.processed_signals.append({
                'signal': signal,
                'lot_size': lot_size,
                'order': order_result
            })
            
            # Afficher le nouveau statut du risque après l'ordre
            print("\n📊 Statut du risque après l'ordre:")
            self.risk_manager.display_risk_status(self.order_sender)
        
        return order_result
    
    def get_account_summary(self):
        """
        Affiche un résumé complet du compte et des positions.
        """
        print("\n" + "=" * 80)
        print("RÉSUMÉ DU COMPTE DE TRADING")
        print("=" * 80)
        
        # Informations du compte
        account_info = self.order_sender.get_account_info()
        if account_info:
            print(f"Compte MT5: {account_info['login']}")
            print(f"Balance: {account_info['balance']:.2f} {account_info['currency']}")
            print(f"Equity: {account_info['equity']:.2f} {account_info['currency']}")
            print(f"Marge libre: {account_info['free_margin']:.2f} {account_info['currency']}")
        
        # Positions ouvertes
        positions = self.order_sender.get_open_positions()
        print(f"\nPositions ouvertes: {len(positions)}")
        
        if positions:
            for i, pos in enumerate(positions, 1):
                profit_loss = "+" if pos.profit >= 0 else ""
                print(f"  {i}. {pos.symbol} - {pos.type_str} - {pos.volume} lots - P&L: {profit_loss}{pos.profit:.2f}")
        
        # Statistiques de risque
        self.risk_manager.display_risk_status(self.order_sender)
        
        # Historique des signaux traités
        print(f"Signaux traités: {len(self.processed_signals)}")
        print("=" * 80 + "\n")
    
    def shutdown(self):
        """
        Ferme proprement les connexions.
        """
        self.order_sender.close_connection()
        print("Bot de trading arrêté")

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le bot avec un risque total de 300 EUR pour 3 positions
    # et une limite de risque de 7% du capital
    bot = TradingBot(total_risk_eur=300.0, max_risk_percentage=7.0)
    
    try:
        # Afficher le résumé initial du compte
        bot.get_account_summary()
        
        # Exemple de signal de trading
        signal_text = """
        EURUSD SELL
        Entry: 1.0850
        SL: 1.0900
        TP1: 1.0800
        TP2: 1.0750
        """
        
        print("🚀 Traitement du signal de trading...")
        result = bot.process_signal(signal_text)
        
        if result:
            print("\n✅ Signal traité avec succès!")
            print(f"ID Ordre MT5: {result.get('mt5_order_id', 'N/A')}")
        else:
            print("\n❌ Échec du traitement du signal.")
        
        # Afficher le résumé final
        bot.get_account_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
    finally:
        bot.shutdown()