import asyncio
from telethon import TelegramClient, events
from config import config
from chatGpt import chatGpt
from order import SendOrder
from riskManager import RiskManager
import re

class TradingBot:
    def __init__(self, risk_per_signal_eur, account_type, telegram_account=None):
        # Configuration Telegram
        if telegram_account is None:
            telegram_account = "MAT"  # Par défaut
        
        telegram_creds = config.get_telegram_credentials(telegram_account)
        self.api_id = telegram_creds['api_id']
        self.api_hash = telegram_creds['api_hash']
        self.session_name = telegram_creds['session_name']
        self.telegram_account = telegram_account.upper()
        
        # Configuration MT5
        self.account_type = account_type.upper()
        
        # IDs des canaux
        self.channel_1_id = config.TELEGRAM_CHANNEL_1_ID
        self.channel_2_id = config.TELEGRAM_CHANNEL_2_ID
        
        # Composants
        self.client = None
        self.order_sender = SendOrder(account_type)
        self.risk_manager = RiskManager(risk_per_signal_eur)
        
    async def start(self):
        """Démarre le bot."""
        print(f"🚀 Démarrage du bot...")
        print(f"📱 Telegram: Compte {self.telegram_account}")
        print(f"📈 MT5: Compte {self.account_type}")
        
        # Connexion Telegram
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start()
        
        if not await self.client.is_user_authorized():
            print("❌ Pas autorisé sur Telegram")
            return False
        
        me = await self.client.get_me()
        print(f"✅ Connecté Telegram: {me.first_name} (Compte {self.telegram_account})")
        
        # Vérifier MT5
        if not self.order_sender.is_connected:
            print(f"❌ MT5 non connecté sur le compte {self.account_type}")
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
            message_text = event.message.text
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
        
        print(f"🎧 Écoute active sur {self.telegram_account} → {self.account_type}...")
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
            
            # 5. Calculer les tailles de lot
            lot_sizes = self.risk_manager.calculate_lot_sizes(orders)
            
            # 6. Placer les ordres sur le compte spécifié
            print(f"📈 Placement des ordres sur le compte {self.account_type}...")
            results = self.order_sender.place_orders(orders, lot_sizes)
            
            if results:
                print(f"🎉 {len(results)} ordres placés sur {self.account_type}!")
            else:
                print(f"❌ Échec placement ordres sur {self.account_type}")
                
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
                print(f"💡 Bot actif ({self.telegram_account} → {self.account_type})... Ctrl+C pour arrêter")
                await self.client.run_until_disconnected()
            except KeyboardInterrupt:
                print("\n⏹️ Arrêt du bot")
            finally:
                self.order_sender.close_connection()

def get_account_selection():
    """Demande le choix du compte MT5 à l'utilisateur."""
    print("\n📈 SÉLECTION DU COMPTE MT5")
    print("=" * 30)
    print("1. MAT   - Compte MAT")
    print("2. DID   - Compte DID") 
    print("3. DEMO  - Compte Démo")
    print("=" * 30)
    
    while True:
        try:
            choice = input("Choisir le compte MT5 (1/2/3): ").strip()
            
            if choice == '1':
                return 'MAT'
            elif choice == '2':
                return 'DID'
            elif choice == '3':
                return 'DEMO'
            else:
                print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3")
                
        except KeyboardInterrupt:
            print("\n❌ Annulé")
            exit()

def get_telegram_account_selection():
    """Demande le choix du compte Telegram à l'utilisateur."""
    print("\n📱 SÉLECTION DU COMPTE TELEGRAM")
    print("=" * 35)
    print("1. MAT   - Compte Telegram MAT")
    print("2. DID   - Compte Telegram DID")
    print("=" * 35)
    
    while True:
        try:
            choice = input("Choisir le compte Telegram (1/2): ").strip()
            
            if choice == '1':
                return 'MAT'
            elif choice == '2':
                return 'DID'
            else:
                print("❌ Choix invalide. Veuillez entrer 1 ou 2")
                
        except KeyboardInterrupt:
            print("\n❌ Annulé")
            exit()

def get_risk_input():
    """Demande le risque à l'utilisateur."""
    while True:
        try:
            risk = input("💰 Quel risque par signal (en €) ? : ")
            risk_value = float(risk)
            
            if risk_value <= 0:
                print("❌ Le risque doit être positif")
                continue
            
            if risk_value > 1000:
                confirm = input(f"⚠️ Risque élevé ({risk_value}€). Confirmer ? (oui/non): ")
                if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
                    continue
            
            return risk_value
            
        except ValueError:
            print("❌ Veuillez entrer un nombre valide")
        except KeyboardInterrupt:
            print("\n❌ Annulé")
            exit()

async def main():
    print("🤖 SYSTÈME DE TRADING TELEGRAM")
    print("=" * 40)
    
    # Sélection du compte Telegram
    telegram_account = get_telegram_account_selection()
    print(f"✅ Compte Telegram sélectionné: {telegram_account}")
    
    # Sélection du compte MT5
    mt5_account = get_account_selection()
    print(f"✅ Compte MT5 sélectionné: {mt5_account}")
    
    # Demander le risque
    risk_per_signal = get_risk_input()
    
    print(f"\n✅ Configuration:")
    print(f"📱 Telegram: {telegram_account}")
    print(f"📈 MT5: {mt5_account}")
    print(f"💰 Risque: {risk_per_signal}€ par signal")
    print(f"📊 Répartition: {risk_per_signal/3:.2f}€ par position")
    print("🔄 Arrondi: Toujours à l'inférieur")
    print("🛡️ Garantie: Risque jamais dépassé")
    
    # Confirmation finale
    print(f"\n⚠️ Les ordres seront passés sur le compte MT5 {mt5_account}")
    print(f"⚠️ En utilisant le compte Telegram {telegram_account}")
    confirm = input("Continuer ? (oui/non): ").lower().strip()
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Lancement annulé")
        return
    
    # Lancer le bot
    bot = TradingBot(risk_per_signal, mt5_account, telegram_account)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())