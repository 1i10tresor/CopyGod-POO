from signalPaser import SignalProcessor
from riskManager import RiskManager
from order import SendOrder

class TradingBot:
    def __init__(self, total_risk_eur, max_risk_percentage=7.0):
        """
        Initialise le bot de trading.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un signal (3 positions)
            max_risk_percentage (float): Pourcentage maximum du capital à risquer
        """
        self.risk_manager = RiskManager(total_risk_eur, max_risk_percentage)
        self.order_sender = SendOrder()
        self.processed_signals = []
        self.supported_channels = [1, 2]
    
    def process_signal(self, signal_text, channel_id=1):
        """
        Traite un signal de trading complet selon le canal spécifié.
        
        Args:
            signal_text (str): Texte du signal à traiter
            channel_id (int): ID du canal (1 ou 2)
        
        Returns:
            list: Liste des ordres placés ou None si échec
        """
        if channel_id not in self.supported_channels:
            print(f"Canal {channel_id} non supporté. Canaux supportés: {self.supported_channels}")
            return None
        
        # Créer un objet signal simulé
        class MockSignal:
            def __init__(self, text):
                self.text = text
        
        mock_signal = MockSignal(signal_text)
        
        # 1. Vérifier si c'est un signal valide
        processor = SignalProcessor(mock_signal, channel_id)
        if not processor.is_signal():
            print("Le texte ne contient pas de signal de trading valide.")
            return None
        
        # 2. Extraire et valider le signal
        signals = processor.get_signal()
        if not signals:
            print("Impossible d'extraire ou de valider le signal.")
            return None
        
        print(f"Signal(s) extrait(s) pour le canal {channel_id}:")
        if isinstance(signals, list):
            for i, sig in enumerate(signals, 1):
                print(f"  Ordre {i}: {sig}")
        else:
            print(f"  {signals}")
        
        # 3. Vérifier le statut du risque AVANT de continuer
        print(f"\n🔍 Vérification du risque du compte (Canal {channel_id})...")
        self.risk_manager.display_risk_status(self.order_sender)
        
        if not self.risk_manager.can_open_position(self.order_sender):
            print("❌ Signal ignoré: Risque du compte trop élevé")
            return None
        
        # 4. Calculer les tailles de lot
        print(f"\n📊 Calcul des tailles de lot pour le canal {channel_id}...")
        lot_sizes = self.risk_manager.calculate_lot_size_for_signal(signals, channel_id)
        
        if not lot_sizes:
            print("Impossible de calculer les tailles de lot")
            return None
        
        print(f"Tailles de lot calculées: {lot_sizes}")
        
        # 5. Placer les ordres sur MT5
        print(f"\n📈 Placement des ordres sur MT5 (Canal {channel_id})...")
        order_results = self.order_sender.place_signal_orders(signals, lot_sizes, channel_id)
        
        if order_results:
            # Enregistrer le signal traité
            signal_record = {
                'channel_id': channel_id,
                'signals': signals,
                'lot_sizes': lot_sizes,
                'orders': order_results,
                'timestamp': order_results[0]['timestamp'] if order_results else None
            }
            self.processed_signals.append(signal_record)
            
            # Afficher le nouveau statut du risque
            print(f"\n📊 Statut du risque après traitement du signal (Canal {channel_id}):")
            self.risk_manager.display_risk_status(self.order_sender)
            
            print(f"✅ Signal du canal {channel_id} traité avec succès! {len(order_results)} ordres placés.")
        else:
            print(f"❌ Échec du traitement du signal du canal {channel_id}.")
        
        return order_results
    
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
        if self.processed_signals:
            print("Détail des signaux:")
            for i, signal_record in enumerate(self.processed_signals, 1):
                channel = signal_record['channel_id']
                orders_count = len(signal_record['orders'])
                print(f"  {i}. Canal {channel} - {orders_count} ordres - {signal_record['timestamp']}")
        
        print("=" * 80 + "\n")
    
    def shutdown(self):
        """
        Ferme proprement les connexions.
        """
        self.order_sender.close_connection()
        print("Bot de trading arrêté")

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le bot avec un risque total de 300 EUR par signal
    # et une limite de risque de 7% du capital
    bot = TradingBot(total_risk_eur=300.0, max_risk_percentage=7.0)
    
    try:
        # Afficher le résumé initial du compte
        bot.get_account_summary()
        
        # Exemple de signal du canal 1
        signal_canal_1 = """
        XAUUSD BUY NOW @ 2329.79
        SL @ 2314.90
        TP1 @ 2350.00
        TP2 @ 2375.00
        TP3 @ 2403.50
        """
        
        print("🚀 Traitement du signal Canal 1...")
        result_1 = bot.process_signal(signal_canal_1, channel_id=1)
        
        if result_1:
            print(f"\n✅ Signal Canal 1 traité avec succès! {len(result_1)} ordres placés.")
        else:
            print("\n❌ Échec du traitement du signal Canal 1.")
        
        # Exemple de signal du canal 2 (simulé)
        signal_canal_2 = """
        EURUSD SELL
        Entry 1: 1.0850
        Entry 2: 1.0860
        Entry 3: 1.0870
        SL: 1.0900
        """
        
        print("\n🚀 Traitement du signal Canal 2...")
        result_2 = bot.process_signal(signal_canal_2, channel_id=2)
        
        if result_2:
            print(f"\n✅ Signal Canal 2 traité avec succès! {len(result_2)} ordres placés.")
        else:
            print("\n❌ Échec du traitement du signal Canal 2.")
        
        # Afficher le résumé final
        bot.get_account_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
    finally:
        bot.shutdown()