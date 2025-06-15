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
        
        # Configuration des canaux
        self.channel_config = {
            1: {
                'name': 'Canal Standard',
                'description': '3 TPs différents, même entrée',
                'format': 'SYMBOL DIRECTION @ ENTRY, SL @ XX, TP1 @ XX, TP2 @ XX, TP3 @ XX'
            },
            2: {
                'name': 'Canal Fourchette', 
                'description': '3 entrées différentes, RR fixes',
                'format': 'DIRECTION XXXX-XX, TP XXXX, SL XX'
            }
        }
    
    def process_signal(self, signal_text, channel_id=1):
        """
        Traite un signal de trading complet selon le canal spécifié.
        
        Args:
            signal_text (str): Texte du signal à traiter
            channel_id (int): ID du canal (1 ou 2) - DOIT ÊTRE SPÉCIFIÉ
        
        Returns:
            list: Liste des ordres placés ou None si échec
        """
        if channel_id not in self.supported_channels:
            print(f"❌ Canal {channel_id} non supporté. Canaux supportés: {self.supported_channels}")
            return None
        
        print(f"🔄 Traitement du signal pour le {self.channel_config[channel_id]['name']} (Canal {channel_id})")
        print(f"📝 Format attendu: {self.channel_config[channel_id]['format']}")
        
        # Créer un objet signal simulé
        class MockSignal:
            def __init__(self, text):
                self.text = text
        
        mock_signal = MockSignal(signal_text)
        
        # 1. Vérifier si c'est un signal valide
        processor = SignalProcessor(mock_signal, channel_id)
        if not processor.is_signal():
            print("❌ Le texte ne contient pas de signal de trading valide.")
            return None
        
        # 2. Extraire et valider le signal
        signals = processor.get_signal()
        if not signals:
            print("❌ Impossible d'extraire ou de valider le signal.")
            return None
        
        print(f"✅ Signal(s) extrait(s) pour le canal {channel_id}:")
        if isinstance(signals, list):
            for i, sig in enumerate(signals, 1):
                print(f"  📊 Ordre {i}: {sig}")
        else:
            print(f"  📊 {signals}")
        
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
            print("❌ Impossible de calculer les tailles de lot")
            return None
        
        print(f"✅ Tailles de lot calculées: {lot_sizes}")
        
        # 5. Placer les ordres sur MT5
        print(f"\n📈 Placement des ordres sur MT5 (Canal {channel_id})...")
        order_results = self.order_sender.place_signal_orders(signals, lot_sizes, channel_id)
        
        if order_results:
            # Enregistrer le signal traité
            signal_record = {
                'channel_id': channel_id,
                'channel_name': self.channel_config[channel_id]['name'],
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
    
    def auto_detect_channel(self, signal_text):
        """
        Tente de détecter automatiquement le canal basé sur le format du signal.
        
        Args:
            signal_text (str): Texte du signal
            
        Returns:
            int: ID du canal détecté (1 ou 2) ou None si indéterminé
        """
        import re
        
        # Patterns pour détecter le canal 2 (fourchettes)
        fourchette_patterns = [
            r'\d{4}-\d{1,2}',  # Format 3349-52
            r'go\s+(buy|sell)\s+\d{4}-\d{1,2}',  # "go sell 3349-52"
            r'(buy|sell)\s+\d{4}-\d{1,2}',  # "sell 3349-52"
        ]
        
        # Patterns pour détecter le canal 1 (format standard)
        canal_1_patterns = [
            r'tp1.*tp2.*tp3',  # Présence de TP1, TP2, TP3
            r'@.*sl.*@.*tp.*@',  # Format avec @ multiples
            r'(buy|sell)\s+(now|market)\s*@',  # "BUY NOW @"
        ]
        
        signal_lower = signal_text.lower()
        
        # Vérifier les patterns du canal 2
        for pattern in fourchette_patterns:
            if re.search(pattern, signal_lower):
                print(f"🔍 Canal 2 détecté (pattern: fourchette)")
                return 2
        
        # Vérifier les patterns du canal 1
        for pattern in canal_1_patterns:
            if re.search(pattern, signal_lower):
                print(f"🔍 Canal 1 détecté (pattern: standard)")
                return 1
        
        print("⚠️  Canal non détecté automatiquement")
        return None
    
    def process_signal_auto(self, signal_text):
        """
        Traite un signal en détectant automatiquement le canal.
        
        Args:
            signal_text (str): Texte du signal à traiter
            
        Returns:
            list: Liste des ordres placés ou None si échec
        """
        # Tentative de détection automatique
        detected_channel = self.auto_detect_channel(signal_text)
        
        if detected_channel:
            print(f"🎯 Canal {detected_channel} détecté automatiquement")
            return self.process_signal(signal_text, detected_channel)
        else:
            print("❌ Impossible de détecter le canal automatiquement")
            print("💡 Veuillez spécifier le canal manuellement:")
            print("   - Canal 1: Format standard avec TP1, TP2, TP3")
            print("   - Canal 2: Format fourchette (ex: 3349-52)")
            return None
    
    def display_channel_info(self):
        """
        Affiche les informations sur les canaux supportés.
        """
        print("\n" + "=" * 80)
        print("CANAUX DE TRADING SUPPORTÉS")
        print("=" * 80)
        
        for channel_id, config in self.channel_config.items():
            print(f"\n📡 CANAL {channel_id} - {config['name']}")
            print(f"   Description: {config['description']}")
            print(f"   Format: {config['format']}")
        
        print("\n" + "=" * 80)
        print("UTILISATION:")
        print("  bot.process_signal(signal_text, channel_id=1)  # Canal spécifique")
        print("  bot.process_signal_auto(signal_text)           # Détection automatique")
        print("=" * 80 + "\n")
    
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
                channel_name = signal_record['channel_name']
                orders_count = len(signal_record['orders'])
                print(f"  {i}. {channel_name} (Canal {channel}) - {orders_count} ordres - {signal_record['timestamp']}")
        
        print("=" * 80 + "\n")
    
    def shutdown(self):
        """
        Ferme proprement les connexions.
        """
        self.order_sender.close_connection()
        print("🔴 Bot de trading arrêté")

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le bot avec un risque total de 300 EUR par signal
    # et une limite de risque de 7% du capital
    bot = TradingBot(total_risk_eur=300.0, max_risk_percentage=7.0)
    
    try:
        # Afficher les informations sur les canaux
        bot.display_channel_info()
        
        # Afficher le résumé initial du compte
        bot.get_account_summary()
        
        # Exemple de signal du canal 1 (SPÉCIFIÉ MANUELLEMENT)
        signal_canal_1 = """
        XAUUSD BUY NOW @ 2329.79
        SL @ 2314.90
        TP1 @ 2350.00
        TP2 @ 2375.00
        TP3 @ 2403.50
        """
        
        print("🚀 Traitement du signal Canal 1 (spécifié manuellement)...")
        result_1 = bot.process_signal(signal_canal_1, channel_id=1)
        
        # Exemple de signal du canal 2 (SPÉCIFIÉ MANUELLEMENT)
        signal_canal_2 = """
        go sell 3349-52
        tp 3330
        sl 54.5
        """
        
        print("\n🚀 Traitement du signal Canal 2 (spécifié manuellement)...")
        result_2 = bot.process_signal(signal_canal_2, channel_id=2)
        
        # Exemple avec détection automatique
        print("\n🤖 Test de détection automatique...")
        
        signal_auto_1 = "EURUSD BUY NOW @ 1.0850, SL @ 1.0800, TP1 @ 1.0900, TP2 @ 1.0950, TP3 @ 1.1000"
        result_auto_1 = bot.process_signal_auto(signal_auto_1)
        
        signal_auto_2 = "go buy 1850-55, tp 1870, sl 45"
        result_auto_2 = bot.process_signal_auto(signal_auto_2)
        
        # Afficher le résumé final
        bot.get_account_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
    finally:
        bot.shutdown()