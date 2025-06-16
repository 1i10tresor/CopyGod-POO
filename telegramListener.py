._process_message(message_text, channel_id, message_id, sender, event.message.date)
                
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
            if info.get('verified_id') == chat_id:
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
                'telegram_chat_id': self.monitored_channels[channel_id]['verified_id'],
                'original_telegram_id': self.monitored_channels[channel_id]['telegram_id'],
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
            'total_processed': len(self.processed_messages),
            'accessible_channels': [
                channel_id for channel_id, info in self.monitored_channels.items()
                if info.get('verified_id') is not None
            ]
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
        print(f"Canaux accessibles: {len(status['accessible_channels'])}/{len(self.monitored_channels)}")
        
        print("\nCanaux surveillés:")
        for channel_id, info in status['monitored_channels'].items():
            verified_id = info.get('verified_id')
            original_id = info['telegram_id']
            status_icon = "✅" if verified_id else "❌"
            
            print(f"  {status_icon} Canal {channel_id} ({info['name']}): {info['message_count']} messages")
            print(f"      ID original: {original_id}")
            if verified_id:
                print(f"      ID vérifié: {verified_id}")
                if info['last_message_time']:
                    print(f"      Dernier message: {info['last_message_time']}")
            else:
                print(f"      ❌ Non accessible")
        
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