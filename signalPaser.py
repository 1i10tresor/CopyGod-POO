import re
from chatGpt import chatGpt

class SignalProcessor:
    def __init__(self, signal, channel_id=1):
        self.signal_text = signal.text
        self.channel_id = channel_id

    def is_signal(self):
        """Vérifie si le texte contient un signal de trading valide."""
        sl = r'.*(sl|stop\s*loss|stop).*'
        tp = r'.*(tp|take\s*profit|take|profit).*'
        return bool(re.search(sl, self.signal_text, re.IGNORECASE) and 
                   re.search(tp, self.signal_text, re.IGNORECASE))
    
    def get_signal(self):
        """Extrait le signal via ChatGPT et le transforme en 3 signaux individuels."""
        # Obtenir la réponse de ChatGPT
        gpt_response = chatGpt(self.signal_text, self.channel_id).get_signal()
        
        if not gpt_response:
            return None
        
        # Valider la structure de base
        if not self._validate_gpt_response(gpt_response):
            return None
        
        # Transformer en 3 signaux individuels
        individual_signals = self._create_individual_signals(gpt_response)
        
        # Valider chaque signal individuel
        validated_signals = []
        for i, signal in enumerate(individual_signals):
            if self._validate_signal_logic(signal):
                # Ajuster le prix d'entrée
                signal['entry_price'] = round(signal['entry_price'] + 0.01, 5)
                validated_signals.append(signal)
            else:
                print(f"Signal {i+1} invalide")
        
        return validated_signals if len(validated_signals) == 3 else None
    
    def _validate_gpt_response(self, response):
        """Valide que la réponse de ChatGPT contient tous les champs requis."""
        required_fields = ['symbol', 'sens', 'sl', 'entry_prices', 'tps']
        
        for field in required_fields:
            if field not in response or response[field] is None:
                print(f"Champ manquant dans la réponse ChatGPT: {field}")
                return False
        
        if response['sens'] not in ['BUY', 'SELL']:
            print(f"Sens invalide: {response['sens']}")
            return False
        
        if len(response['entry_prices']) != 3 or len(response['tps']) != 3:
            print("Doit avoir exactement 3 prix d'entrée et 3 TPs")
            return False
        
        return True
    
    def _create_individual_signals(self, gpt_response):
        """Transforme la réponse ChatGPT en 3 signaux individuels."""
        signals = []
        
        for i in range(3):
            signal = {
                'symbol': gpt_response['symbol'],
                'sens': gpt_response['sens'],
                'entry_price': gpt_response['entry_prices'][i],
                'sl': gpt_response['sl'],
                'tp': gpt_response['tps'][i],
                'order_index': i + 1
            }
            signals.append(signal)
        
        return signals
    
    def _validate_signal_logic(self, signal):
        """Valide la cohérence d'un signal individuel."""
        try:
            sens = signal['sens']
            entry_price = signal['entry_price']
            sl_price = signal['sl']
            tp_price = signal['tp']
            
            # Vérifier que tous les prix sont des nombres
            if not all(isinstance(x, (int, float)) for x in [entry_price, sl_price, tp_price]):
                print("Tous les prix doivent être des nombres")
                return False
            
            # Logique de validation pour BUY
            if sens == 'BUY':
                if sl_price >= entry_price:
                    print(f"BUY: SL ({sl_price}) doit être < entry ({entry_price})")
                    return False
                if tp_price <= entry_price:
                    print(f"BUY: TP ({tp_price}) doit être > entry ({entry_price})")
                    return False
            
            # Logique de validation pour SELL
            elif sens == 'SELL':
                if sl_price <= entry_price:
                    print(f"SELL: SL ({sl_price}) doit être > entry ({entry_price})")
                    return False
                if tp_price >= entry_price:
                    print(f"SELL: TP ({tp_price}) doit être < entry ({entry_price})")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la validation du signal: {e}")
            return False