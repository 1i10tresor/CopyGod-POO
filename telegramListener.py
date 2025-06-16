import asyncio
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from config import telegram_config
from main import TradingBot
from signalPaser import SignalProcessor

class TelegramListener:
    """
    Écouteur Telegram en temps réel utilisant Telethon.
    Se connecte directement avec votre compte utilisateur.
    """
    
    def __init__(self, bot_instance):
        """
        Initialise l'écouteur Telegram.
        
        Args:
            bot_instance (TradingBot): Instance du bot de trading
        """
        self.bot = bot_instance
        self.client = None
        self.is_listening = False
        
        # Configuration des canaux surveillés
        self.monitored_channels = {
            1: {
                'name': 'Canal Standard',
                'telegram_id': telegram_config.get_channel_id(1),
                'message_count': 0,
                'last_message_time': None
            },
            2: {
                'name': 'Canal Fourchette',
                'telegram_id': telegram_config.get_channel_id(2),
                'message_count': 0,
                'last_message_time': None
            }
        }
        
        # Historique des messages traités
        self.processed_messages = []
        
        # Configuration Telegram
        self.api_id = telegram_config.API_ID
        self.api_hash = telegram_config.API_HASH
        self.session_name = telegram_config.SESSION_NAME
    
    async def initialize_client(self):
        """
        Initialise et connecte le client Telegram.
        """
        try:
            print("🔄 Initialisation du client Telegram...")
            
            # Créer le client Telethon
            self.client = TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash
            )
            
            # Se connecter
            await self.client.start()
            
            # Vérifier si on est connecté
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                print(f"✅ Connecté en tant que: {me.first_name} (@{me.username})")
                
                # Vérifier l'accès aux canaux
                await self._verify_channel_access()
                
                return True
            else:
                print("❌ Échec de l'autorisation Telegram")
                return False
                
        except SessionPasswordNeededError:
            print("❌ Authentification à deux facteurs requise")
            print("💡 Veuillez configurer votre session Telegram manuellement")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation Telegram: {e}")
            return False
    
    async def _verify_channel_access(self):
        """
        Vérifie l'accès aux canaux surveillés.
        """
        print("🔍 Vérification de l'accès aux canaux...")
        
        for channel_id, info in self.monitored_channels.items():
            telegram_id = info['telegram_id']
            try:
                # Essayer d'obtenir les informations du canal
                entity = await self.client.get_entity(telegram_id)
                print(f"✅ Canal {channel_id} ({info['name']}): {entity.title}")
                
                # Obtenir les derniers messages pour tester
                messages = await self.client.get_messages(entity, limit=1)
                if messages:
                    print(f"   📨 Dernier message: {messages[0].date}")
                
            except Exception as e:
                print(f"❌ Erreur d'accès au canal {channel_id} (ID: {telegram_id}): {e}")
                print(f"💡 Vérifiez que vous avez accès à ce canal")
    
    async def start_listening(self):
        """
        Démarre l'écoute en temps réel des messages.
        """
        if self.is_listening:
            print("⚠️  L'écouteur est déjà en cours d'exécution")
            return
        
        # Initialiser le client si nécessaire
        if not self.client:
            if not await self.initialize_client():
                print("❌ Impossible de démarrer l'écoute")
                return
        
        print("🎧 Démarrage de l'écoute en temps réel...")
        print("📡 Canaux surveillés:")
        for channel_id, info in self.monitored_channels.items():
            print(f"   Canal {channel_id}: {info['name']} (TG: {info['telegram_id']})")
        
        self.is_listening = True
        
        # Configurer les gestionnaires d'événements
        await self._setup_event_handlers()
        
        print("✅ Écouteur Telegram démarré!")
        print("💡 En attente de nouveaux messages...")
    
    async def _setup_event_handlers(self):
        """
        Configure les gestionnaires d'événements pour les nouveaux messages.
        """
        # Liste des IDs de canaux à surveiller
        channel_ids = [info['telegram_id'] for info in self.monitored_channels.values()]
        
        @self.client.on(events.NewMessage(chats=channel_ids))
        async def handle_new_message(event):
            """
            Gestionnaire pour les nouveaux messages.
            """
            try:
                # Identifier le canal source
                channel_id = self._identify_channel(event.chat_id)
                if not channel_id:
                    return
                
                message_text = event.message.message
                message_id = event.message.id
                sender = await event.get_sender()
                
                print(f"\n🆕 Nouveau message détecté dans le Canal {channel_id}")
                print(f"📝 ID: {message_id}")
                print(f"📡 Chat ID: {event.chat_id}")
                print(f"👤 Expéditeur: {sender.first_name if sender else 'Inconnu'}")
                print(f"⏰ Timestamp: {event.message.date}")
                print(f"💬 Contenu:\n{message_text}")
                
                # Traiter le message
                await self._process_message(message_text, channel_id, message_id, sender, event.message.date)
                
            except Exception as e:
                print(f"❌ Erreur lors du traitement du message: {e}")
    
    def _identify_channel(self, chat_id):
        """
        Identifie le canal source à partir de l'ID du chat.
        
        Args:
            chat_id (int): ID du chat Telegram
        
        Returns:
            int: Numéro du canal (1 ou 2) ou None si non trouvé
        """
        for channel_id, info in self.monitored_channels.items():
            if info['telegram_id'] == chat_id:
                return channel_id
        return None
    
    async def _process_message(self, message_text, channel_id, message_id, sender, timestamp):
        """
        Traite un nouveau message détecté.
        
        Args:
            message_text (str): Contenu du message
            channel_id (int): ID du canal source
            message_id (int): ID du message Telegram
            sender: Expéditeur du message
            timestamp: Timestamp du message
        """
        try:
            # Vérifier si le message contient un signal
            class MockSignal:
                def __init__(self, text):
                    self.text = text
            
            mock_signal = MockSignal(message_text)
            processor = SignalProcessor(mock_signal, channel_id)
            
            if not processor.is_signal():
                print(f"ℹ️  Message ignoré: ne contient pas de signal de trading")
                return
            
            print(f"✅ Signal détecté! Lancement du traitement...")
            
            # Traiter le signal avec le bot
            result = self.bot.process_signal(message_text, channel_id)
            
            # Enregistrer le message traité
            processed_record = {
                'message_id': message_id,
                'channel_id': channel_id,
                'channel_name': self.monitored_channels[channel_id]['name'],
                'telegram_chat_id': self.monitored_channels[channel_id]['telegram_id'],
                'content': message_text,
                'timestamp': timestamp.isoformat(),
                'sender': sender.first_name if sender else 'Inconnu',
                'processing_result': result is not None,
                'orders_placed': len(result) if result else 0,
                'processed_at': datetime.now().isoformat()
            }
            
            self.processed_messages.append(processed_record)
            self.monitored_channels[channel_id]['message_count'] += 1
            self.monitored_channels[channel_id]['last_message_time'] = timestamp.isoformat()
            
            if result:
                print(f"🎉 Message traité avec succès! {len(result)} ordres placés.")
            else:
                print(f"❌ Échec du traitement du message.")
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement du message: {e}")
    
    async def stop_listening(self):
        """
        Arrête l'écoute des messages.
        """
        if not self.is_listening:
            print("⚠️  L'écouteur n'est pas en cours d'exécution")
            return
        
        print("🔇 Arrêt de l'écouteur Telegram...")
        self.is_listening = False
        
        if self.client:
            await self.client.disconnect()
            print("✅ Client Telegram déconnecté")
    
    def get_listener_status(self):
        """
        Retourne le statut de l'écouteur.
        """
        return {
            'is_listening': self.is_listening,
            'client_connected': self.client is not None and self.client.is_connected(),
            'monitored_channels': self.monitored_channels,
            'total_processed': len(self.processed_messages)
        }
    
    def display_listener_summary(self):
        """
        Affiche un résumé de l'activité de l'écouteur.
        """
        print("\n" + "=" * 80)
        print("RÉSUMÉ DE L'ÉCOUTEUR TELEGRAM")
        print("=" * 80)
        
        status = self.get_listener_status()
        print(f"Statut: {'🟢 ACTIF' if status['is_listening'] else '🔴 ARRÊTÉ'}")
        print(f"Client: {'🟢 Connecté' if status['client_connected'] else '🔴 Déconnecté'}")
        print(f"Messages traités: {status['total_processed']}")
        
        print("\nCanaux surveillés:")
        for channel_id, info in status['monitored_channels'].items():
            print(f"  📡 Canal {channel_id} ({info['name']}): {info['message_count']} messages")
            print(f"      Telegram ID: {info['telegram_id']}")
            if info['last_message_time']:
                print(f"      Dernier message: {info['last_message_time']}")
        
        if self.processed_messages:
            print(f"\nDerniers messages traités:")
            for record in self.processed_messages[-5:]:  # 5 derniers
                status_icon = "✅" if record['processing_result'] else "❌"
                print(f"  {status_icon} Canal {record['channel_id']} - {record['orders_placed']} ordres - {record['processed_at']}")
        
        print("=" * 80 + "\n")


class TradingSystemTelegram:
    """
    Système de trading complet avec intégration Telegram temps réel.
    """
    
    def __init__(self, total_risk_eur=None, max_risk_percentage=None):
        """
        Initialise le système de trading avec Telegram.
        """
        self.bot = TradingBot(total_risk_eur, max_risk_percentage)
        self.telegram_listener = TelegramListener(self.bot)
        self.is_running = False
    
    async def start_system(self):
        """
        Démarre le système complet (bot + écouteur Telegram).
        """
        print("🚀 Démarrage du système de trading avec Telegram...")
        
        # Afficher les configurations
        telegram_config.display_config()
        
        # Afficher les informations sur les canaux
        self.bot.display_channel_info()
        
        # Afficher le résumé du compte
        self.bot.get_account_summary()
        
        # Démarrer l'écouteur Telegram
        await self.telegram_listener.start_listening()
        
        self.is_running = True
        print("✅ Système de trading démarré avec succès!")
        print("💡 Le système surveille maintenant les canaux Telegram en temps réel.")
    
    async def stop_system(self):
        """
        Arrête le système complet.
        """
        print("🛑 Arrêt du système de trading...")
        
        # Arrêter l'écouteur Telegram
        await self.telegram_listener.stop_listening()
        
        # Fermer les connexions du bot
        self.bot.shutdown()
        
        self.is_running = False
        print("✅ Système de trading arrêté")
    
    async def run_forever(self):
        """
        Maintient le système en vie indéfiniment.
        """
        try:
            print("💡 Système en cours d'exécution... Appuyez sur Ctrl+C pour arrêter")
            
            while self.is_running:
                await asyncio.sleep(10)  # Vérification toutes les 10 secondes
                
                # Afficher un statut périodique (optionnel)
                if int(time.time()) % 300 == 0:  # Toutes les 5 minutes
                    print(f"💓 Système actif - {datetime.now().strftime('%H:%M:%S')}")
                    
        except KeyboardInterrupt:
            print("\n⏹️  Arrêt du système demandé par l'utilisateur")
        except Exception as e:
            print(f"\n💥 Erreur inattendue: {e}")
        finally:
            await self.stop_system()
    
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
            'telegram_status': self.telegram_listener.get_listener_status()
        }
    
    def display_full_summary(self):
        """
        Affiche un résumé complet du système.
        """
        print("\n" + "=" * 100)
        print("RÉSUMÉ COMPLET DU SYSTÈME DE TRADING TELEGRAM")
        print("=" * 100)
        
        # Statut du système
        status = self.get_system_status()
        print(f"Système: {'🟢 ACTIF' if status['system_running'] else '🔴 ARRÊTÉ'}")
        
        # Résumé du bot
        self.bot.get_account_summary()
        
        # Résumé de l'écouteur Telegram
        self.telegram_listener.display_listener_summary()
        
        print("=" * 100 + "\n")


# Fonction principale pour lancer le système
async def main():
    """
    Fonction principale pour lancer le système de trading Telegram.
    """
    # Créer le système
    system = TradingSystemTelegram()
    
    try:
        # Démarrer le système
        await system.start_system()
        
        # Maintenir le système en vie
        await system.run_forever()
        
    except Exception as e:
        print(f"💥 Erreur dans le système principal: {e}")
    finally:
        await system.stop_system()


# Point d'entrée
if __name__ == "__main__":
    # Lancer le système avec asyncio
    asyncio.run(main())