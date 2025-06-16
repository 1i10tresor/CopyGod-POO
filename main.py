from signalPaser import SignalProcessor
from riskManager import RiskManager
from order import SendOrder
from config import telegram_config, trading_config
import MetaTrader5 as mt5

class TradingBot:
    def __init__(self, total_risk_eur=None, max_risk_percentage=None):
        """
        Initialise le bot de trading.
        
        Args:
            total_risk_eur (float): Risque total en EUR pour un signal (3 positions)
            max_risk_percentage (float): Pourcentage maximum du capital à risquer
        """
        # Utiliser la configuration ou les paramètres fournis
        self.total_risk_eur = total_risk_eur or trading_config.TOTAL_RISK_EUR
        self.max_risk_percentage = max_risk_percentage or trading_config.MAX_RISK_PERCENTAGE
        
        print("🤖 Initialisation du bot de trading...")
        print("🔄 Connexion à MetaTrader 5...")
        
        # Initialiser les composants
        self.order_sender = SendOrder()
        
        # Vérifier que la connexion MT5 est établie avant de continuer
        if not self.order_sender.is_connected:
            print("❌ Impossible de démarrer le bot sans connexion MT5")
            raise Exception("Connexion MT5 requise")
        
        # Vérifier que nous sommes bien sur le compte démo
        if not self.order_sender.verify_demo_connection():
            print("❌ Connexion au compte démo non confirmée")
            raise Exception("Compte démo requis pour la sécurité")
        
        print("✅ Bot de trading initialisé avec succès")
        
        # Initialiser les autres composants
        self.risk_manager = RiskManager(self.total_risk_eur, self.max_risk_percentage)
        self.processed_signals = []
        self.supported_channels = [1, 2]
        
        # Configuration des canaux avec IDs Telegram
        self.channel_config = {
            1: {
                'name': 'Canal Standard',
                'description': '3 TPs différents, même entrée',
                'format': 'SYMBOL DIRECTION @ ENTRY, SL @ XX, TP1 @ XX, TP2 @ XX, TP3 @ XX',
                'telegram_id': telegram_config.get_channel_id(1)
            },
            2: {
                'name': 'Canal Fourchette', 
                'description': '3 entrées différentes, RR fixes',
                'format': 'DIRECTION XXXX-XX, TP XXXX, SL XX',
                'telegram_id': telegram_config.get_channel_id(2)
            }
        }
    
    def process_signal(self, signal_text, channel_id):
        """
        Traite un signal de trading complet selon le canal spécifié.
        
        Args:
            signal_text (str): Texte du signal à traiter
            channel_id (int): ID du canal (1 ou 2) - OBLIGATOIRE
        
        Returns:
            list: Liste des ordres placés ou None si échec
        """
        if channel_id not in self.supported_channels:
            print(f"❌ Canal {channel_id} non supporté. Canaux supportés: {self.supported_channels}")
            return None
        
        print(f"🔄 Traitement du signal pour le {self.channel_config[channel_id]['name']} (Canal {channel_id})")
        print(f"📝 Format attendu: {self.channel_config[channel_id]['format']}")
        
        # VÉRIFICATION OBLIGATOIRE du compte démo avant traitement
        print("🔍 Vérification de la connexion au compte démo...")
        if not self.order_sender.verify_demo_connection():
            print("🚫 TRAITEMENT ANNULÉ - Connexion au compte démo non confirmée")
            return None
        
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
        
        # 5. Placer les ordres sur MT5 (avec vérification démo intégrée)
        print(f"\n📈 Placement des ordres sur MT5 (Canal {channel_id})...")
        order_results = self.order_sender.place_signal_orders(signals, lot_sizes, channel_id)
        
        if order_results:
            # Enregistrer le signal traité
            signal_record = {
                'channel_id': channel_id,
                'channel_name': self.channel_config[channel_id]['name'],
                'telegram_id': self.channel_config[channel_id]['telegram_id'],
                'signals': signals,
                'lot_sizes': lot_sizes,
                'orders': order_results,
                'timestamp': order_results[0]['timestamp'] if order_results else None,
                'account_type': 'DEMO'
            }
            self.processed_signals.append(signal_record)
            
            # Afficher le nouveau statut du risque
            print(f"\n📊 Statut du risque après traitement du signal (Canal {channel_id}):")
            self.risk_manager.display_risk_status(self.order_sender)
            
            print(f"✅ Signal du canal {channel_id} traité avec succès! {len(order_results)} ordres placés.")
        else:
            print(f"❌ Échec du traitement du signal du canal {channel_id}.")
        
        return order_results
    
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
            print(f"   Telegram ID: {config['telegram_id']}")
        
        print("\n" + "=" * 80)
        print("UTILISATION:")
        print("  bot.process_signal(signal_text, channel_id=1)  # Canal spécifique OBLIGATOIRE")
        print("=" * 80 + "\n")
    
    def _get_position_type_string(self, position_type):
        """
        Convertit le type de position MT5 en string lisible.
        
        Args:
            position_type (int): Type de position MT5
            
        Returns:
            str: Type de position en string
        """
        if position_type == mt5.ORDER_TYPE_BUY:
            return "BUY"
        elif position_type == mt5.ORDER_TYPE_SELL:
            return "SELL"
        else:
            return f"TYPE_{position_type}"
    
    def get_account_summary(self):
        """
        Affiche un résumé complet du compte et des positions.
        """
        print("\n" + "=" * 80)
        print("RÉSUMÉ DU COMPTE DE TRADING")
        print("=" * 80)
        
        # Vérifier la connexion démo avant d'afficher les informations
        if not self.order_sender.verify_demo_connection():
            print("❌ Impossible d'afficher le résumé - Connexion au compte démo non confirmée")
            return
        
        # Informations du compte
        account_info = self.order_sender.get_account_info()
        if account_info:
            print(f"Compte MT5: {account_info['login']}")
            print(f"Nom: {account_info['name']}")
            print(f"Serveur: {account_info['server']}")
            print(f"Mode: {'🟢 DÉMO' if account_info['is_demo'] else '🔴 RÉEL'}")
            print(f"Balance: {account_info['balance']:.2f} {account_info['currency']}")
            print(f"Equity: {account_info['equity']:.2f} {account_info['currency']}")
            print(f"Marge libre: {account_info['free_margin']:.2f} {account_info['currency']}")
        
        # Positions ouvertes
        positions = self.order_sender.get_open_positions()
        print(f"\nPositions ouvertes: {len(positions)}")
        
        if positions:
            for i, pos in enumerate(positions, 1):
                # Utiliser notre fonction pour convertir le type
                position_type = self._get_position_type_string(pos.type)
                profit_loss = "+" if pos.profit >= 0 else ""
                print(f"  {i}. {pos.symbol} - {position_type} - {pos.volume} lots - P&L: {profit_loss}{pos.profit:.2f}")
        
        # Statistiques de risque
        self.risk_manager.display_risk_status(self.order_sender)
        
        # Historique des signaux traités
        print(f"Signaux traités: {len(self.processed_signals)}")
        if self.processed_signals:
            print("Détail des signaux:")
            for i, signal_record in enumerate(self.processed_signals, 1):
                channel = signal_record['channel_id']
                channel_name = signal_record['channel_name']
                telegram_id = signal_record['telegram_id']
                orders_count = len(signal_record['orders'])
                account_type = signal_record.get('account_type', 'UNKNOWN')
                print(f"  {i}. {channel_name} (Canal {channel}, TG: {telegram_id}) - {orders_count} ordres - {account_type} - {signal_record['timestamp']}")
        
        print("=" * 80 + "\n")
    
    def shutdown(self):
        """
        Ferme proprement les connexions.
        """
        self.order_sender.close_connection()
        print("🔴 Bot de trading arrêté")