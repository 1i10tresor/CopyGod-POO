import re
from chatGpt import chatGpt

class SignalProcessor:
    def __init__(self, signal, channel_id=1):
        """
        Initialise le processeur de signal.
        
        Args:
            signal: Objet signal contenant le texte
            channel_id (int): ID du canal (1 ou 2)
        """
        self.signal_text = signal.text
        self.channel_id = channel_id

    def is_signal(self):
        """
        Vérifie si le texte contient un signal de trading valide.
        """
        sl = r'.*(sl|stop\s*loss|stop).*'
        tp = r'.*(tp|take\s*profit|take|profit).*'
        if re.search(sl, self.signal_text, re.IGNORECASE) and re.search(tp, self.signal_text, re.IGNORECASE):
            return True
        return False
    
    def get_signal(self):
        """
        Extrait et valide le signal selon le type de canal.
        """
        # Passer l'ID du canal à ChatGPT pour qu'il sache quel format traiter
        signal = chatGpt(self.signal_text, self.channel_id).get_signal()
        
        if not signal:
            return None
        
        if self.channel_id == 1:
            return self._process_channel_1(signal)
        elif self.channel_id == 2:
            return self._process_channel_2(signal)
        else:
            print(f"Canal {self.channel_id} non supporté")
            return None
    
    def _process_channel_1(self, signal):
        """
        Traite un signal du canal 1 (format standard avec 3 TPs).
        """
        # Vérifier et corriger le signal pour le canal 1
        validated_signal = self._validate_channel_1_signal(signal)
        return validated_signal
    
    def _process_channel_2(self, signal):
        """
        Traite un signal du canal 2 (3 prix d'entrée, RR fixe).
        """
        # Adapter le signal pour le canal 2
        adapted_signal = self._adapt_channel_2_signal(signal)
        return adapted_signal
    
    def _validate_channel_1_signal(self, signal):
        """
        Valide et corrige un signal du canal 1.
        """
        if not self._check_basic_signal(signal):
            return None
        
        # S'assurer qu'il y a exactement 3 TPs
        tps = signal.get('tps', [])
        if len(tps) < 3:
            print("Signal du canal 1 doit avoir 3 TPs")
            return None
        
        # Gérer le cas où TP3 est "open"
        if isinstance(tps[2], str) and tps[2].lower() == 'open':
            tps[2] = self._calculate_open_tp(signal, tps)
        
        signal['tps'] = tps[:3]  # Garder seulement les 3 premiers TPs
        
        # Validation finale
        if self._validate_signal_logic(signal):
            return signal
        return None
    
    def _adapt_channel_2_signal(self, signal):
        """
        Adapte un signal pour le canal 2 (3 entrées, RR fixe).
        """
        if not self._check_basic_signal_canal_2(signal):
            return None
        
        # Pour le canal 2, on doit avoir 3 prix d'entrée
        entry_prices = signal.get('entry_prices', [])
        if not entry_prices or len(entry_prices) < 3:
            # Si pas assez de prix d'entrée, utiliser le prix principal
            base_entry = signal.get('entry_price')
            if not base_entry:
                print("Canal 2 nécessite des prix d'entrée multiples")
                return None
            entry_prices = [base_entry, base_entry, base_entry]
        
        # Calculer les TPs basés sur les RR (2.5, 4, 6)
        sl_price = signal['sl']
        sens = signal['sens']
        
        adapted_signals = []
        rr_ratios = [2.5, 4, 6]
        
        for i, (entry_price, rr) in enumerate(zip(entry_prices[:3], rr_ratios)):
            # Calculer la distance SL
            sl_distance = abs(entry_price - sl_price)
            
            # Calculer le TP basé sur le RR
            if sens == 'BUY':
                tp_price = entry_price + (sl_distance * rr)
            else:  # SELL
                tp_price = entry_price - (sl_distance * rr)
            
            # Créer un signal adapté pour chaque entrée
            adapted_signal = {
                'symbol': signal['symbol'],
                'sens': sens,
                'entry_price': entry_price,
                'sl': sl_price,
                'tps': [tp_price],  # Un seul TP par ordre pour le canal 2
                'order_index': i + 1,
                'rr_ratio': rr
            }
            
            adapted_signals.append(adapted_signal)
        
        return adapted_signals
    
    def _calculate_open_tp(self, signal, tps):
        """
        Calcule le TP3 quand il est marqué comme "open".
        TP3 = 2 fois la distance du TP2.
        """
        try:
            entry_price = signal['entry_price']
            tp2 = tps[1]
            
            # Distance entre entry et TP2
            tp2_distance = abs(tp2 - entry_price)
            
            # TP3 = 2 fois cette distance
            if signal['sens'] == 'BUY':
                tp3 = entry_price + (2 * tp2_distance)
            else:  # SELL
                tp3 = entry_price - (2 * tp2_distance)
            
            return tp3
            
        except Exception as e:
            print(f"Erreur lors du calcul du TP3 'open': {e}")
            return tps[1] * 1.5  # Valeur de secours
    
    def _check_basic_signal(self, signal):
        """
        Vérifie les champs de base d'un signal pour le canal 1.
        """
        if signal is None:
            return False
        
        required_fields = ['symbol', 'sens', 'entry_price', 'sl']
        for field in required_fields:
            if field not in signal or signal[field] is None:
                print(f"Champ manquant: {field}")
                return False
        
        if signal['sens'] not in ['BUY', 'SELL']:
            print(f"Sens invalide: {signal['sens']}")
            return False
        
        return True
    
    def _check_basic_signal_canal_2(self, signal):
        """
        Vérifie les champs de base d'un signal pour le canal 2.
        """
        if signal is None:
            return False
        
        required_fields = ['symbol', 'sens', 'sl']
        for field in required_fields:
            if field not in signal or signal[field] is None:
                print(f"Champ manquant: {field}")
                return False
        
        if signal['sens'] not in ['BUY', 'SELL']:
            print(f"Sens invalide: {signal['sens']}")
            return False
        
        # Pour le canal 2, on doit avoir soit entry_price soit entry_prices
        if 'entry_price' not in signal and 'entry_prices' not in signal:
            print("Canal 2 nécessite des prix d'entrée")
            return False
        
        return True
    
    def _validate_signal_logic(self, signal):
        """
        Valide la logique du signal (prix cohérents).
        """
        try:
            sens = signal['sens']
            entry_price = signal['entry_price']
            sl_price = signal['sl']
            tps = signal['tps']
            
            # Vérifier que tps est une liste
            if not isinstance(tps, list) or len(tps) == 0:
                print("TPs invalides")
                return False
            
            # Vérifier que tous les tps sont des nombres
            for tp in tps:
                if not isinstance(tp, (int, float)):
                    print(f"TP invalide: {tp}")
                    return False
            
            # Logique de validation pour BUY
            if sens == 'BUY':
                if sl_price >= entry_price:
                    print(f"BUY: SL ({sl_price}) doit être < entry ({entry_price})")
                    return False
                for i, tp in enumerate(tps):
                    if tp <= entry_price:
                        print(f"BUY: TP{i+1} ({tp}) doit être > entry ({entry_price})")
                        return False
            
            # Logique de validation pour SELL
            elif sens == 'SELL':
                if sl_price <= entry_price:
                    print(f"SELL: SL ({sl_price}) doit être > entry ({entry_price})")
                    return False
                for i, tp in enumerate(tps):
                    if tp >= entry_price:
                        print(f"SELL: TP{i+1} ({tp}) doit être < entry ({entry_price})")
                        return False
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la validation du signal: {e}")
            return False