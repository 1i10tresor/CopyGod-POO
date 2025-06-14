import re
from chatGpt import chatGpt

class SignalProcessor:
    def __init__(self, signal):
        self.signal_text = signal.text

    def is_signal(self):
        sl = r'.*(sl|stop\s*loss|stop).*'
        tp = r'.*(tp|take\s*profit|take|profit).*'
        if re.search(sl, self.signal_text) and re.search(tp, self.signal_text):
            return True
        return False
    
    def get_signal(self):
        signal = chatGpt(self.signal_text).get_signal()
        return signal(signal)
    
    def check_signal(self, signal):
        if signal == None:
            return False    
        for key in signal.keys():
            if signal[key] == None:
                return False
        sens = signal['sens']
        if sens != 'BUY' and sens != 'SELL':
            return False
        if sens == 'BUY':
            if signal['entry_price'] > signal['sl'] or signal['entry_price'] > any(signal['tps']):
                return False
        if sens == 'SELL':
            if signal['entry_price'] < signal['sl'] or signal['entry_price'] < any(signal['tps']):
                return False
        return signal
        


    