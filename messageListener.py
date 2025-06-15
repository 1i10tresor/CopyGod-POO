import time
import threading
from datetime import datetime
from main import TradingBot

class MessageListener:
    """
    Écouteur de messages pour les canaux de trading.
    Surveille les nouveaux messages et déclenche le traitement automatique.
    """
    
    def __init__(self, bot_instance):
        """
        Initialise l'écouteur de messages.
        
        Args:
            bot_instance (TradingBot): Instance du bot de trading
        """
        self.bot = bot_instance
        self.is_listening = False
        self.listener_thread = None
        
        # Configuration des canaux surveillés
        self.monitored_channels = {
            1: {
                'name': 'Canal Standard',
                'last_message_id': None,
                'message_count': 0
            },
            2: {
                'name': 'Canal Fourchette',
                'last_message_id': None,
                'message_count': 0
            }
        }
        
        # Historique des messages traités
        self.processed_messages = []
    
    def start_listening(self):
        """
        Démarre l'écoute des messages en arrière-plan.
        """
        if self.is_listening:
            print("⚠️  L'écouteur est déjà en cours d'exécution")
            return
        
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        
        print("🎧 Écouteur de messages démarré")
        print(f"📡 Surveillance des canaux: {list(self.monitored_channels.keys())}")
    
    def stop_listening(self):
        """
        Arrête l'écoute des messages.
        """
        if not self.is_listening:
            print("⚠️  L'écouteur n'est pas en cours d'exécution")
            return
        
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=5)
        
        print("🔇 Écouteur de messages arrêté")
    
    def _listen_loop(self):
        """
        Boucle principale d'écoute des messages.
        """
        print("🔄 Démarrage de la boucle d'écoute...")
        
        while self.is_listening:
            try:
                # Vérifier chaque canal surveillé
                for channel_id in self.monitored_channels.keys():
                    new_messages = self._check_channel_for_new_messages(channel_id)
                    
                    if new_messages:
                        for message in new_messages:
                            self._process_new_message(message, channel_id)
                
                # Attendre avant la prochaine vérification
                time.sleep(2)  # Vérification toutes les 2 secondes
                
            except Exception as e:
                print(f"❌ Erreur dans la boucle d'écoute: {e}")
                time.sleep(5)  # Attendre plus longtemps en cas d'erreur
    
    def _check_channel_for_new_messages(self, channel_id):
        """
        Vérifie s'il y a de nouveaux messages dans un canal.
        
        Args:
            channel_id (int): ID du canal à vérifier
            
        Returns:
            list: Liste des nouveaux messages
        """
        # SIMULATION - Dans un vrai système, ceci se connecterait à l'API du canal
        # (Discord, Telegram, etc.)
        
        # Pour la démonstration, on simule des messages
        if hasattr(self, '_demo_messages'):
            return self._get_demo_messages(channel_id)
        
        return []
    
    def _get_demo_messages(self, channel_id):
        """
        Génère des messages de démonstration pour tester le système.
        """
        demo_messages = {
            1: [
                {
                    'id': 'msg_001',
                    'content': 'XAUUSD BUY NOW @ 2329.79\nSL @ 2314.90\nTP1 @ 2350.00\nTP2 @ 2375.00\nTP3 @ 2403.50',
                    'timestamp': datetime.now().isoformat(),
                    'author': 'TradingSignals'
                }
            ],
            2: [
                {
                    'id': 'msg_002',
                    'content': 'go sell 3349-52\ntp 3330\nsl 54.5',
                    'timestamp': datetime.now().isoformat(),
                    'author': 'ForexSignals'
                }
            ]
        }
        
        # Retourner les messages de démonstration une seule fois
        if channel_id in demo_messages and not hasattr(self, f'_demo_sent_{channel_id}'):
            setattr(self, f'_demo_sent_{channel_id}', True)
            return demo_messages[channel_id]
        
        return []
    
    def _process_new_message(self, message, channel_id):
        """
        Traite un nouveau message détecté.
        
        Args:
            message (dict): Données du message
            channel_id (int): ID du canal source
        """
        try:
            message_content = message['content']
            message_id = message['id']
            
            print(f"\n🆕 Nouveau message détecté dans le Canal {channel_id}")
            print(f"📝 ID: {message_id}")
            print(f"👤 Auteur: {message.get('author', 'Inconnu')}")
            print(f"⏰ Timestamp: {message.get('timestamp', 'N/A')}")
            print(f"💬 Contenu:\n{message_content}")
            
            # Vérifier si le message contient un signal
            from signalPaser import SignalProcessor
            
            class MockSignal:
                def __init__(self, text):
                    self.text = text
            
            mock_signal = MockSignal(message_content)
            processor = SignalProcessor(mock_signal, channel_id)
            
            if not processor.is_signal():
                print(f"ℹ️  Message ignoré: ne contient pas de signal de trading")
                return
            
            print(f"✅ Signal détecté! Lancement du traitement...")
            
            # Traiter le signal avec le bot
            result = self.bot.process_signal(message_content, channel_id)
            
            # Enregistrer le message traité
            processed_record = {
                'message_id': message_id,
                'channel_id': channel_id,
                'channel_name': self.monitored_channels[channel_id]['name'],
                'content': message_content,
                'timestamp': message.get('timestamp'),
                'author': message.get('author'),
                'processing_result': result is not None,
                'orders_placed': len(result) if result else 0,
                'processed_at': datetime.now().isoformat()
            }
            
            self.processed_messages.append(processed_record)
            self.monitored_channels[channel_id]['message_count'] += 1
            self.monitored_channels[channel_id]['last_message_id'] = message_id
            
            if result:
                print(f"🎉 Message traité avec succès! {len(result)} ordres placés.")
            else:
                print(f"❌ Échec du traitement du message.")
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement du message: {e}")
    
    def simulate_message(self, channel_id, message_content, author="TestUser"):
        """
        Simule l'arrivée d'un nouveau message pour les tests.
        
        Args:
            channel_id (int): ID du canal
            message_content (str): Contenu du message
            author (str): Auteur du message
        """
        if channel_id not in self.monitored_channels:
            print(f"❌ Canal {channel_id} non surveillé")
            return
        
        # Créer un message simulé
        simulated_message = {
            'id': f'sim_{int(time.time())}_{channel_id}',
            'content': message_content,
            'timestamp': datetime.now().isoformat(),
            'author': author
        }
        
        print(f"🧪 Simulation d'un message dans le Canal {channel_id}")
        self._process_new_message(simulated_message, channel_id)
    
    def get_listener_status(self):
        """
        Retourne le statut de l'écouteur.
        """
        return {
            'is_listening': self.is_listening,
            'monitored_channels': self.monitored_channels,
            'total_processed': len(self.processed_messages),
            'thread_alive': self.listener_thread.is_alive() if self.listener_thread else False
        }
    
    def display_listener_summary(self):
        """
        Affiche un résumé de l'activité de l'écouteur.
        """
        print("\n" + "=" * 80)
        print("RÉSUMÉ DE L'ÉCOUTEUR DE MESSAGES")
        print("=" * 80)
        
        status = self.get_listener_status()
        print(f"Statut: {'🟢 ACTIF' if status['is_listening'] else '🔴 ARRÊTÉ'}")
        print(f"Thread: {'🟢 Vivant' if status['thread_alive'] else '🔴 Arrêté'}")
        print(f"Messages traités: {status['total_processed']}")
        
        print("\nCanaux surveillés:")
        for channel_id, info in status['monitored_channels'].items():
            print(f"  📡 Canal {channel_id} ({info['name']}): {info['message_count']} messages")
            if info['last_message_id']:
                print(f"      Dernier message: {info['last_message_id']}")
        
        if self.processed_messages:
            print(f"\nDerniers messages traités:")
            for record in self.processed_messages[-5:]:  # 5 derniers
                status_icon = "✅" if record['processing_result'] else "❌"
                print(f"  {status_icon} Canal {record['channel_id']} - {record['orders_placed']} ordres - {record['processed_at']}")
        
        print("=" * 80 + "\n")


class TradingSystem:
    """
    Système de trading complet avec écouteur de messages intégré.
    """
    
    def __init__(self, total_risk_eur=300.0, max_risk_percentage=7.0):
        """
        Initialise le système de trading complet.
        """
        self.bot = TradingBot(total_risk_eur, max_risk_percentage)
        self.listener = MessageListener(self.bot)
        self.is_running = False
    
    def start_system(self):
        """
        Démarre le système complet (bot + écouteur).
        """
        print("🚀 Démarrage du système de trading complet...")
        
        # Afficher les informations sur les canaux
        self.bot.display_channel_info()
        
        # Afficher le résumé du compte
        self.bot.get_account_summary()
        
        # Démarrer l'écouteur
        self.listener.start_listening()
        
        self.is_running = True
        print("✅ Système de trading démarré avec succès!")
        print("💡 Le système surveille maintenant les canaux et traite automatiquement les signaux.")
    
    def stop_system(self):
        """
        Arrête le système complet.
        """
        print("🛑 Arrêt du système de trading...")
        
        # Arrêter l'écouteur
        self.listener.stop_listening()
        
        # Fermer les connexions du bot
        self.bot.shutdown()
        
        self.is_running = False
        print("✅ Système de trading arrêté")
    
    def get_system_status(self):
        """
        Retourne le statut complet du système.
        """
        return {
            'system_running': self.is_running,
            'bot_status': {
                'processed_signals': len(self.bot.processed_signals),
                'supported_channels': self.bot.supported_channels
            },
            'listener_status': self.listener.get_listener_status()
        }
    
    def display_full_summary(self):
        """
        Affiche un résumé complet du système.
        """
        print("\n" + "=" * 100)
        print("RÉSUMÉ COMPLET DU SYSTÈME DE TRADING")
        print("=" * 100)
        
        # Statut du système
        status = self.get_system_status()
        print(f"Système: {'🟢 ACTIF' if status['system_running'] else '🔴 ARRÊTÉ'}")
        
        # Résumé du bot
        self.bot.get_account_summary()
        
        # Résumé de l'écouteur
        self.listener.display_listener_summary()
        
        print("=" * 100 + "\n")


# Exemple d'utilisation du système complet
if __name__ == "__main__":
    # Créer le système complet
    system = TradingSystem(total_risk_eur=300.0, max_risk_percentage=7.0)
    
    try:
        # Démarrer le système
        system.start_system()
        
        # Simuler quelques messages pour la démonstration
        print("\n🧪 DÉMONSTRATION - Simulation de messages...")
        
        # Message Canal 1
        signal_1 = """EURUSD BUY NOW @ 1.0850
SL @ 1.0800
TP1 @ 1.0900
TP2 @ 1.0950
TP3 @ 1.1000"""
        
        system.listener.simulate_message(1, signal_1, "SignalProvider1")
        
        time.sleep(3)
        
        # Message Canal 2
        signal_2 = """go sell 1850-55
tp 1830
sl 65"""
        
        system.listener.simulate_message(2, signal_2, "SignalProvider2")
        
        # Attendre un peu pour voir les résultats
        time.sleep(5)
        
        # Afficher le résumé final
        system.display_full_summary()
        
        # Garder le système en vie pour la démonstration
        print("💡 Système en cours d'exécution... Appuyez sur Ctrl+C pour arrêter")
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du système demandé par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
    finally:
        system.stop_system()