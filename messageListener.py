import time
import threading
from datetime import datetime
from main import TradingBot
from config import telegram_config

class MessageListener:
    """
    Écouteur de messages pour les canaux de trading Telegram.
    VERSION SIMULATION UNIQUEMENT - Pour la vraie connexion, utilisez telegramListener.py
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
        
        # Configuration des canaux surveillés avec IDs Telegram
        self.monitored_channels = {
            1: {
                'name': 'Canal Standard',
                'telegram_id': telegram_config.get_channel_id(1),
                'last_message_id': None,
                'message_count': 0
            },
            2: {
                'name': 'Canal Fourchette',
                'telegram_id': telegram_config.get_channel_id(2),
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
        
        print("🎧 Écouteur de messages démarré (MODE SIMULATION)")
        print("💡 Pour la vraie connexion Telegram, utilisez: python launch_telegram_bot.py")
        print("📡 Canaux surveillés:")
        for channel_id, info in self.monitored_channels.items():
            print(f"   Canal {channel_id}: {info['name']} (TG: {info['telegram_id']})")
    
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
        print("⚠️  ATTENTION: Cette version utilise uniquement la simulation")
        print("💡 Pour la vraie connexion Telegram, utilisez telegramListener.py")
        
        while self.is_listening:
            try:
                # Cette version ne fait que de la simulation
                # La vraie connexion Telegram est dans telegramListener.py
                time.sleep(5)  # Attendre 5 secondes
                
            except Exception as e:
                print(f"❌ Erreur dans la boucle d'écoute: {e}")
                time.sleep(5)  # Attendre plus longtemps en cas d'erreur
    
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
            telegram_id = message.get('telegram_id', 'N/A')
            
            print(f"\n🆕 Nouveau message détecté dans le Canal {channel_id}")
            print(f"📝 ID: {message_id}")
            print(f"📡 Telegram ID: {telegram_id}")
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
            
            # Traiter le signal avec le bot (CHANNEL_ID OBLIGATOIRE)
            result = self.bot.process_signal(message_content, channel_id)
            
            # Enregistrer le message traité
            processed_record = {
                'message_id': message_id,
                'channel_id': channel_id,
                'channel_name': self.monitored_channels[channel_id]['name'],
                'telegram_id': telegram_id,
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
    
    def get_listener_status(self):
        """
        Retourne le statut de l'écouteur.
        """
        return {
            'is_listening': self.is_listening,
            'monitored_channels': self.monitored_channels,
            'total_processed': len(self.processed_messages),
            'thread_alive': self.listener_thread.is_alive() if self.listener_thread else False,
            'connection_type': 'SIMULATION'
        }
    
    def display_listener_summary(self):
        """
        Affiche un résumé de l'activité de l'écouteur.
        """
        print("\n" + "=" * 80)
        print("RÉSUMÉ DE L'ÉCOUTEUR DE MESSAGES (MODE SIMULATION)")
        print("=" * 80)
        
        status = self.get_listener_status()
        print(f"Statut: {'🟢 ACTIF' if status['is_listening'] else '🔴 ARRÊTÉ'}")
        print(f"Thread: {'🟢 Vivant' if status['thread_alive'] else '🔴 Arrêté'}")
        print(f"Type: 🧪 {status['connection_type']}")
        print(f"Messages traités: {status['total_processed']}")
        
        print("\nCanaux surveillés:")
        for channel_id, info in status['monitored_channels'].items():
            print(f"  📡 Canal {channel_id} ({info['name']}): {info['message_count']} messages")
            print(f"      Telegram ID: {info['telegram_id']}")
            if info['last_message_id']:
                print(f"      Dernier message: {info['last_message_id']}")
        
        if self.processed_messages:
            print(f"\nDerniers messages traités:")
            for record in self.processed_messages[-5:]:  # 5 derniers
                status_icon = "✅" if record['processing_result'] else "❌"
                print(f"  {status_icon} Canal {record['channel_id']} (TG: {record['telegram_id']}) - {record['orders_placed']} ordres - {record['processed_at']}")
        
        print("\n💡 Pour la vraie connexion Telegram, utilisez:")
        print("   python launch_telegram_bot.py")
        print("=" * 80 + "\n")


class TradingSystem:
    """
    Système de trading complet avec écouteur de messages intégré (MODE SIMULATION).
    """
    
    def __init__(self, total_risk_eur=None, max_risk_percentage=None):
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
        print("🚀 Démarrage du système de trading complet (MODE SIMULATION)...")
        print("💡 Pour la vraie connexion Telegram, utilisez: python launch_telegram_bot.py")
        
        # Afficher les configurations
        telegram_config.display_config()
        
        # Afficher les informations sur les canaux
        self.bot.display_channel_info()
        
        # Afficher le résumé du compte
        self.bot.get_account_summary()
        
        # Démarrer l'écouteur
        self.listener.start_listening()
        
        self.is_running = True
        print("✅ Système de trading démarré avec succès (MODE SIMULATION)!")
        print("💡 Utilisez les fonctions simulate_* pour tester le système.")
    
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
            'connection_type': 'SIMULATION',
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
        print("RÉSUMÉ COMPLET DU SYSTÈME DE TRADING (MODE SIMULATION)")
        print("=" * 100)
        
        # Statut du système
        status = self.get_system_status()
        print(f"Système: {'🟢 ACTIF' if status['system_running'] else '🔴 ARRÊTÉ'}")
        print(f"Type: 🧪 {status['connection_type']}")
        
        # Résumé du bot
        self.bot.get_account_summary()
        
        # Résumé de l'écouteur
        self.listener.display_listener_summary()
        
        print("💡 POUR LA VRAIE CONNEXION TELEGRAM:")
        print("   python launch_telegram_bot.py")
        print("=" * 100 + "\n")