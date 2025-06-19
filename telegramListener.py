import asyncio
from telethon import TelegramClient, events
from config import config
from chatGpt import chatGpt
from order import SendOrder
import re

class TradingBot:
    def __init__(self):
        # Configuration
        self.api_id = config.TELEGRAM_API_ID
        self.api_hash = config.TELEGRAM_API_HASH
        self.session_name = config.TELEGRAM_SESSION_NAME
        
        # IDs des canaux
        self.channel_1_id = -1002125503665
        self.channel_2_id = -1002259371711
        
        # Composants
        self.client = None
        self.order_sender = SendOrder()
        
    async def start(self):
        """Démarre le bot."""
        print("🚀 Démarrage du bot...")
        
        # Connexion Telegram
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start()
        
        if not await self.client.is_user_authorized():
            print("❌ Pas autorisé sur Telegram")
            return False
        
        me = await self.client.get_me()
        print(f"✅ Connecté Telegram: {me.first_name}")
        
        # Vérifier MT5
        if not self.order_sender.is_connected:
            print("❌ MT5 non connecté")
            return False
        
        # Vérifier canaux
        try:
            await self.client.get_entity(self.channel_1_id)
            await self.client.get_entity(self.channel_2_id)
            print("✅ Canaux accessibles")
        except Exception as e:
            print(f"❌ Canaux inaccessibles: {e}")
            return False
        
        # Écouter les messages
        @self.client.on(events.NewMessage(chats=[self.channel_1_id, self.channel_2_id]))
        async def handle_message(event):
            message_text = event.message.message
            chat_id = event.chat_id
            
            # Identifier le canal
            if chat_id == self.channel_1_id:
                channel_id = 1
            elif chat_id == self.channel_2_id:
                channel_id = 2
            else:
                return
            
            print(f"\n📨 Message Canal {channel_id}: {message_text[:50]}...")
            await self.process_message(message_text, channel_id)
        
        print("🎧 Écoute active...")
        return True
    
    async def process_message(self, message_text, channel_id):
        """Traite un message."""
        try:
            # 1. Vérifier si signal (has tp + has sl)
            if not self.has_tp_sl(message_text):
                print("ℹ️ Pas un signal")
                return
            
            print("✅ Signal détecté!")
            
            # 2. Envoyer à ChatGPT
            gpt = chatGpt(message_text, channel_id)
            signal_data = gpt.get_signal()
            
            if not signal_data:
                print("❌ ChatGPT n'a pas pu extraire le signal")
                return
            
            print("✅ Signal extrait par ChatGPT")
            
            # 3. Vérifier cohérence
            if not self.validate_signal(signal_data):
                print("❌ Signal incohérent")
                return
            
            print("✅ Signal validé")
            
            # 4. Créer 3 ordres individuels
            orders = self.create_orders(signal_data)
            
            # 5. Placer les ordres
            results = self.order_sender.place_orders(orders, [0.01, 0.01, 0.01])
            
            if results:
                print(f"🎉 {len(results)} ordres placés!")
            else:
                print("❌ Échec placement ordres")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def has_tp_sl(self, text):
        """Vérifie si le message contient TP et SL."""
        has_tp = bool(re.search(r'(tp|take.?profit)', text, re.IGNORECASE))
        has_sl = bool(re.search(r'(sl|stop.?loss)', text, re.IGNORECASE))
        return has_tp and has_sl
    
    def validate_signal(self, signal_data):
        """Valide la cohérence du signal."""
        try:
            symbol = signal_data['symbol']
            sens = signal_data['sens']
            sl = signal_data['sl']
            entry_prices = signal_data['entry_prices']
            tps = signal_data['tps']
            
            # Vérifier structure
            if not all([symbol, sens, sl, entry_prices, tps]):
                return False
            
            if len(entry_prices) != 3 or len(tps) != 3:
                return False
            
            if sens not in ['BUY', 'SELL']:
                return False
            
            # Vérifier cohérence prix
            for i in range(3):
                entry = entry_prices[i]
                tp = tps[i]
                
                if sens == 'BUY':
                    if sl >= entry or tp <= entry:
                        return False
                else:  # SELL
                    if sl <= entry or tp >= entry:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def create_orders(self, signal_data):
        """Crée 3 ordres individuels."""
        orders = []
        
        for i in range(3):
            order = {
                'symbol': signal_data['symbol'],
                'sens': signal_data['sens'],
                'entry_price': signal_data['entry_prices'][i],
                'sl': signal_data['sl'],
                'tp': signal_data['tps'][i]
            }
            orders.append(order)
        
        return orders
    
    async def run(self):
        """Lance le bot."""
        if await self.start():
            try:
                print("💡 Bot actif... Ctrl+C pour arrêter")
                await self.client.run_until_disconnected()
            except KeyboardInterrupt:
                print("\n⏹️ Arrêt du bot")
            finally:
                self.order_sender.close_connection()

async def main():
    bot = TradingBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())