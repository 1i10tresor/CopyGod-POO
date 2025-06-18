import asyncio
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from config import telegram_config, trading_config
from signalPaser import SignalProcessor
from riskManager import RiskManager
from order import SendOrder

class TradingSystemTelegram:
    def __init__(self):
        # Configuration Telegram
        self.api_id = telegram_config.API_ID
        self.api_hash = telegram_config.API_HASH
        self.session_name = telegram_config.SESSION_NAME
        
        # IDs des canaux (format -100...)
        self.channel_1_id = -1002125503665  # Canal 1
        self.channel_2_id = -1002259371711  # Canal 2
        
        # Composants du système
        self.client = None
        self.order_sender = SendOrder()
        self.risk_manager = RiskManager()
        self.is_running = False
        
        print("🤖 Système de trading initialisé")
    
    async def start_system(self):
        """Démarre le système complet."""
        print("🚀 Démarrage du système...")
        
        # Vérifier MT5
        if not self.order_sender.is_connected:
            print("❌ MT5 non connecté")
            return False
        
        # Initialiser Telegram
        if not await self._initialize_telegram():
            return False
        
        # Vérifier l'accès aux canaux
        if not await self._verify_channels():
            return False
        
        # Démarrer l'écoute
        await self._start_listening()
        
        self.is_running = True
        print("✅ Système démarré avec succès!")
        return True
    
    async def _initialize_telegram(self):
        """Initialise la connexion Telegram."""
        try:
            print("🔄 Connexion à Telegram...")
            
            self.client = TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash
            )
            
            await self.client.start()
            
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                print(f"✅ Connecté: {me.first_name}")
                return True
            else:
                print("❌ Autorisation Telegram échouée")
                return False
                
        except Exception as e:
            print(f"❌ Erreur Telegram: {e}")
            return False
    
    async def _verify_channels(self):
        """Vérifie l'accès aux canaux."""
        try:
            print("🔍 Vérification des canaux...")
            
            # Tester Canal 1
            try:
                entity1 = await self.client.get_entity(self.channel_1_id)
                print(f"✅ Canal 1 accessible: {getattr(entity1, 'title', 'Canal 1')}")
            except Exception as e:
                print(f"❌ Canal 1 inaccessible: {e}")
                return False
            
            # Tester Canal 2
            try:
                entity2 = await self.client.get_entity(self.channel_2_id)
                print(f"✅ Canal 2 accessible: {getattr(entity2, 'title', 'Canal 2')}")
            except Exception as e:
                print(f"❌ Canal 2 inaccessible: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification canaux: {e}")
            return False
    
    async def _start_listening(self):
        """Démarre l'écoute des messages."""
        print("🎧 Démarrage de l'écoute...")
        
        @self.client.on(events.NewMessage(chats=[self.channel_1_id, self.channel_2_id]))
        async def handle_message(event):
            try:
                message_text = event.message.message
                chat_id = event.chat_id
                
                # Identifier le canal
                if chat_id == self.channel_1_id:
                    channel_id = 1
                    channel_name = "Canal 1"
                elif chat_id == self.channel_2_id:
                    channel_id = 2
                    channel_name = "Canal 2"
                else:
                    return
                
                print(f"\n🆕 Message {channel_name}: {message_text[:50]}...")
                
                # Traiter le message
                await self._process_message(message_text, channel_id)
                
            except Exception as e:
                print(f"❌ Erreur traitement message: {e}")
        
        print("✅ Écoute active")
    
    async def _process_message(self, message_text, channel_id):
        """Traite un message avec retry."""
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                print(f"🔄 Tentative {attempt + 1}/{max_retries + 1}")
                await asyncio.sleep(2)
            
            try:
                # 1. Vérifier si c'est un signal
                class MockSignal:
                    def __init__(self, text):
                        self.text = text
                
                processor = SignalProcessor(MockSignal(message_text), channel_id)
                
                if not processor.is_signal():
                    print("ℹ️ Pas un signal de trading")
                    return
                
                # 2. Extraire le signal via ChatGPT
                print(f"🤖 Envoi à ChatGPT (Canal {channel_id})...")
                signals = processor.get_signal()
                
                if not signals or len(signals) != 3:
                    print(f"❌ Tentative {attempt + 1}: Signal invalide")
                    if attempt < max_retries:
                        continue
                    else:
                        print("❌ Toutes les tentatives ont échoué")
                        return
                
                print(f"✅ 3 signaux extraits")
                
                # 3. Vérifier le risque
                account_info = self.order_sender.get_account_info()
                if not account_info:
                    print("❌ Impossible d'obtenir les infos du compte")
                    return
                
                if not self.risk_manager.can_open_position(account_info):
                    print("❌ Risque trop élevé")
                    return
                
                # 4. Calculer les lots
                lot_sizes = self.risk_manager.calculate_lot_sizes(signals)
                
                # 5. Placer les ordres
                print("📈 Placement des ordres...")
                results = self.order_sender.place_orders(signals, lot_sizes)
                
                if results and len(results) > 0:
                    print(f"🎉 {len(results)} ordres placés avec succès!")
                    return
                else:
                    print(f"❌ Tentative {attempt + 1}: Tous les ordres ont échoué")
                    if attempt < max_retries:
                        continue
                    else:
                        print("❌ Échec final après toutes les tentatives")
                        return
                
            except Exception as e:
                print(f"❌ Erreur tentative {attempt + 1}: {e}")
                if attempt < max_retries:
                    continue
                else:
                    print("❌ Échec final")
                    return
    
    async def run_forever(self):
        """Maintient le système en vie."""
        try:
            print("💡 Système actif... Ctrl+C pour arrêter")
            
            while self.is_running:
                await asyncio.sleep(60)  # Vérification chaque minute
                
        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé")
        except Exception as e:
            print(f"\n💥 Erreur: {e}")
        finally:
            await self.stop_system()
    
    async def stop_system(self):
        """Arrête le système."""
        print("🛑 Arrêt du système...")
        
        self.is_running = False
        
        if self.client:
            await self.client.disconnect()
        
        self.order_sender.close_connection()
        
        print("✅ Système arrêté")

# Fonction principale
async def main():
    system = TradingSystemTelegram()
    
    if await system.start_system():
        await system.run_forever()
    else:
        print("❌ Impossible de démarrer le système")

if __name__ == "__main__":
    asyncio.run(main())