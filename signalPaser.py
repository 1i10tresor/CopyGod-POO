import re
from chatGpt import chatGpt

class SignalProcessor:
    def __init__(self, signal):
        self.signal_text = signal.text

    def is_signal(self):
        sl = r'.*(sl|stop\s*loss|stop).*'
        tp = r'.*(tp|take\s*profit|take|profit).*'
        if re.search(sl, self.signal_text, re.IGNORECASE) and re.search(tp, self.signal_text, re.IGNORECASE):
            return True
        return False
    
    def get_signal(self):
        signal = chatGpt(self.signal_text).get_signal()
        return self.check_signal(signal)
    
    def check_signal(self, signal):
        if signal is None:
            return False
        
        # Vérifier que tous les champs obligatoires sont présents
        required_fields = ['symbol', 'sens', 'entry_price', 'sl', 'tps']
        for field in required_fields:
            if field not in signal or signal[field] is None:
                return False
        
        sens = signal['sens']
        if sens not in ['BUY', 'SELL']:
            return False
        
        entry_price = signal['entry_price']
        sl_price = signal['sl']
        tps = signal['tps']
        
        # Vérifier que tps est une liste
        if not isinstance(tps, list) or len(tps) == 0:
            return False
        
        # Vérifier que tous les tps sont des nombres
        for tp in tps:
            if not isinstance(tp, (int, float)):
                return False
        
        # Logique de validation pour BUY
        if sens == 'BUY':
            # Pour un BUY: SL < entry_price < TPs
            if sl_price >= entry_price:
                return False
            for tp in tps:
                if tp <= entry_price:
                    return False
        
        # Logique de validation pour SELL
        if sens == 'SELL':
            # Pour un SELL: TPs < entry_price < SL
            if sl_price <= entry_price:
                return False
            for tp in tps:
                if tp >= entry_price:
                    return False
        
        return signal