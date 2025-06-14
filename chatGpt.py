import openai
from info import Infos
import dotenv
import os
import re
import json

class chatGpt():
    def __init__(self, signal):
        dotenv.load_dotenv()
        self.gpt_key = os.getenv("GPT_KEY")
        self.signal = signal
        self.prompt = f"""
            Analyse le message de trading suivant et extrais les informations essentielles au format JSON strict.

            ## Consignes :
            1. Format de sortie : Uniquement du JSON valide, sans texte supplémentaire
            2. Champs obligatoires :
            - symbol (en majuscules, ex: "BTCUSDT"). Il doit correspondre au symbole d'une paire de trading, ex: XAUUSD, BTCUSD, EURUSD
            - sens ("BUY" ou "SELL")
            - entry_price (nombre)
            - sl (nombre)
            - tps (tableau, même avec un seul TP)
            3. Si information manquante : utiliser `null`
            4. Normalisation :
            - "long"/"achat" → "BUY"
            - "short"/"vente" → "SELL"
            - Convertir "k"/"M" (ex: "50k" → 50000)

            ## Exemple de sortie :
            {{
            "symbol": "ETHUSDT",
            "sens": "SELL",
            "entry_price": 3421.50,
            "sl": 3450.00,
            "tps": [3400.00, 3380.00]
            }}

            ## Message à analyser :
            \"\"\"
            {self.signal}
            \"\"\"

            ## Variantes acceptées :
            - Symboles : "BTC/USDT" → "BTCUSDT"
            - Stop loss : "SL", "stop", "stop-loss"
            - Take profit : "TP", "target", "take-profit"

            Résultat JSON :
            """

    def get_signal(self):
        try:
            openai.api_key = self.gpt_key
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": self.prompt}],
                timeout=30
            )
            return self.signal_cleaner(response)
        except Exception as e:
            return e
    
    @staticmethod
    def signal_cleaner(response):
        try:
            match = re.search(r'\{.*?\}', response.choices[0].message.content, re.DOTALL)
            if match:
                signal = json.loads(match.group(0))
                return signal
            return None
        except Exception as e:
            return e