class SimulatedSignal:
    """
    Classe pour créer des signaux simulés pour les tests.
    """
    
    def __init__(self, text, channel_id=1, author="TestUser", message_id=None):
        """
        Initialise un signal simulé.
        
        Args:
            text (str): Contenu du signal
            channel_id (int): ID du canal (1 ou 2)
            author (str): Auteur du message
            message_id (str): ID du message (généré automatiquement si None)
        """
        self.text = text
        self.channel_id = channel_id
        self.author = author
        self.message_id = message_id or f"sim_{int(time.time())}_{channel_id}"
        self.timestamp = datetime.now().isoformat()
    
    def to_message_format(self):
        """
        Convertit le signal en format message pour l'écouteur.
        
        Returns:
            dict: Message formaté
        """
        return {
            'id': self.message_id,
            'content': self.text,
            'timestamp': self.timestamp,
            'author': self.author,
            'channel_id': self.channel_id
        }


class SignalLibrary:
    """
    Bibliothèque de signaux prédéfinis pour les tests.
    """
    
    # Signaux du Canal 1 (Format standard)
    CANAL_1_SIGNALS = {
        'xauusd_buy': """XAUUSD BUY NOW @ 2329.79
SL @ 2314.90
TP1 @ 2350.00
TP2 @ 2375.00
TP3 @ 2403.50""",
        
        'eurusd_buy': """EURUSD BUY NOW @ 1.0850
SL @ 1.0800
TP1 @ 1.0900
TP2 @ 1.0950
TP3 @ 1.1000""",
        
        'gbpusd_sell': """GBPUSD SELL NOW @ 1.2500
SL @ 1.2550
TP1 @ 1.2400
TP2 @ 1.2350
TP3 @ 1.2300""",
        
        'xauusd_buy_open': """XAUUSD BUY NOW @ 2300.00
SL @ 2280.00
TP1 @ 2320.00
TP2 @ 2340.00
TP3 @ open"""
    }
    
    # Signaux du Canal 2 (Format fourchette)
    CANAL_2_SIGNALS = {
        'xauusd_sell_fourchette': """go sell 3349-52
tp 3330
sl 54.5""",
        
        'eurusd_buy_fourchette': """go buy 1850-55
tp 1870
sl 45""",
        
        'gbpusd_sell_fourchette': """sell 2100-10
tp 2080
sl 115""",
        
        'btcusd_buy_fourchette': """buy 45000-50
tp 46000
sl 800"""
    }
    
    @classmethod
    def get_signal(cls, signal_name, channel_id=None):
        """
        Récupère un signal prédéfini.
        
        Args:
            signal_name (str): Nom du signal
            channel_id (int): ID du canal (détecté automatiquement si None)
        
        Returns:
            SimulatedSignal: Signal simulé ou None si non trouvé
        """
        # Chercher dans les signaux du canal 1
        if signal_name in cls.CANAL_1_SIGNALS:
            text = cls.CANAL_1_SIGNALS[signal_name]
            channel = channel_id or 1
            return SimulatedSignal(text, channel, f"Canal1Bot")
        
        # Chercher dans les signaux du canal 2
        if signal_name in cls.CANAL_2_SIGNALS:
            text = cls.CANAL_2_SIGNALS[signal_name]
            channel = channel_id or 2
            return SimulatedSignal(text, channel, f"Canal2Bot")
        
        print(f"Signal '{signal_name}' non trouvé")
        return None
    
    @classmethod
    def list_signals(cls):
        """
        Liste tous les signaux disponibles.
        """
        print("\n📋 SIGNAUX DISPONIBLES")
        print("=" * 50)
        
        print("\n📡 Canal 1 (Format Standard):")
        for name in cls.CANAL_1_SIGNALS.keys():
            print(f"  - {name}")
        
        print("\n📡 Canal 2 (Format Fourchette):")
        for name in cls.CANAL_2_SIGNALS.keys():
            print(f"  - {name}")
        
        print("\n💡 Usage: SignalLibrary.get_signal('signal_name')")
        print("=" * 50)
    
    @classmethod
    def create_test_sequence(cls):
        """
        Crée une séquence de test avec différents signaux.
        
        Returns:
            list: Liste de signaux simulés
        """
        test_signals = [
            cls.get_signal('xauusd_buy'),
            cls.get_signal('xauusd_sell_fourchette'),
            cls.get_signal('eurusd_buy'),
            cls.get_signal('eurusd_buy_fourchette'),
            cls.get_signal('xauusd_buy_open')
        ]
        
        return [signal for signal in test_signals if signal is not None]


# Exemple d'utilisation
if __name__ == "__main__":
    import time
    from datetime import datetime
    
    # Lister tous les signaux disponibles
    SignalLibrary.list_signals()
    
    # Créer un signal simulé
    signal = SignalLibrary.get_signal('xauusd_buy')
    if signal:
        print(f"\n📝 Signal créé:")
        print(f"Canal: {signal.channel_id}")
        print(f"Auteur: {signal.author}")
        print(f"Contenu:\n{signal.text}")
        
        # Convertir en format message
        message = signal.to_message_format()
        print(f"\n📨 Format message: {message}")
    
    # Créer une séquence de test
    print(f"\n🧪 Séquence de test:")
    test_sequence = SignalLibrary.create_test_sequence()
    for i, sig in enumerate(test_sequence, 1):
        print(f"  {i}. Canal {sig.channel_id} - {sig.author}")