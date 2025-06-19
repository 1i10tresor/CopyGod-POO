from openai import OpenAI
from config import config
import re
import json

class chatGpt():
    def __init__(self, signal, channel_id=1):
        self.gpt_key = config.GPT_KEY
        self.signal = signal
        self.channel_id = channel_id
        
        # Initialiser le client OpenAI
        self.client = OpenAI(api_key=self.gpt_key)
        
        # Prompts spécifiques pour chaque canal
        if channel_id == 1:
            self.prompt = self._get_channel_1_prompt()
        elif channel_id == 2:
            self.prompt = self._get_channel_2_prompt()
        else:
            raise ValueError(f"Canal {channel_id} non supporté")

    def _get_channel_1_prompt(self):
        return f"""
        Analyse ce signal de trading du CANAL 1 et retourne UNIQUEMENT un JSON valide.

        RÈGLES STRICTES:
        1. Format de sortie: JSON uniquement, sans texte supplémentaire
        2. Structure obligatoire:
        {{
            "symbol": "SYMBOLE_EN_MAJUSCULES",
            "sens": "BUY" ou "SELL",
            "sl": nombre,
            "entry_prices": [prix1, prix2, prix3],
            "tps": [tp1, tp2, tp3]
        }}

        CANAL 1 - LOGIQUE:
        - Si un seul prix d'entrée: le dupliquer 3 fois dans entry_prices
        - Toujours 3 TPs différents
        - Si TP3 = "open": calculer comme 2x la distance du TP2

        NORMALISATION:
        - "long"/"achat" → "BUY"
        - "short"/"vente" → "SELL"
        - Symboles: "BTC/USDT" → "BTCUSDT", "XAU/USD" → "XAUUSD"

        EXEMPLE DE SORTIE:
        {{
            "symbol": "XAUUSD",
            "sens": "BUY",
            "sl": 2314.90,
            "entry_prices": [2329.79, 2329.79, 2329.79],
            "tps": [2350.00, 2375.00, 2403.50]
        }}

        Signal à analyser:
        "{self.signal}"
        """

    def _get_channel_2_prompt(self):
        return f"""
        Analyse ce signal de trading du CANAL 2 et retourne UNIQUEMENT un JSON valide.

        RÈGLES STRICTES:
        1. Format de sortie: JSON uniquement, sans texte supplémentaire
        2. Structure obligatoire:
        {{
            "symbol": "SYMBOLE_EN_MAJUSCULES",
            "sens": "BUY" ou "SELL",
            "sl": nombre,
            "entry_prices": [prix1, prix2, prix3],
            "tps": [tp1, tp2, tp3]
        }}

        CANAL 2 - LOGIQUE SPÉCIALE:
        - Format fourchette "3349-52" → [3349, 3350.5, 3352]
        - SL abrégé "54.5" avec base "33" → 3354.5
        - 3 TPs identiques (un seul TP donné, répété 3 fois)

        TRANSFORMATION FOURCHETTE:
        - "3349-52" = de 3349 à 3352
        - Générer: [prix_bas, prix_milieu, prix_haut]
        - Milieu = (bas + haut) / 2

        SL ABRÉGÉ:
        - Base = premiers chiffres avant tiret
        - Si SL < 100: base + SL
        - Si SL ≥ 100: utiliser tel quel

        EXEMPLE DE SORTIE:
        {{
            "symbol": "XAUUSD",
            "sens": "SELL",
            "sl": 3354.5,
            "entry_prices": [3349, 3350.5, 3352],
            "tps": [3330, 3330, 3330]
        }}

        Signal à analyser:
        "{self.signal}"
        """

    def get_signal(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": self.prompt}],
                timeout=30
            )
            return self.signal_cleaner(response)
        except Exception as e:
            print(f"Erreur ChatGPT: {e}")
            return None
    
    @staticmethod
    def signal_cleaner(response):
        try:
            content = response.choices[0].message.content
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                signal = json.loads(match.group(0))
                return signal
            return None
        except Exception as e:
            print(f"Erreur lors du nettoyage du signal: {e}")
            return None