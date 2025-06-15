import openai
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
            - symbol (en majuscules, ex: "BTCUSDT", "XAUUSD"). Il doit correspondre au symbole d'une paire de trading
            - sens ("BUY" ou "SELL")
            - entry_price (nombre) ou entry_prices (tableau pour plusieurs entrées)
            - sl (nombre)
            - tps (tableau, toujours 3 éléments pour le canal 1)
            3. Si information manquante : utiliser `null`
            4. Normalisation :
            - "long"/"achat" → "BUY"
            - "short"/"vente" → "SELL"
            - Convertir "k"/"M" (ex: "50k" → 50000)
            - "NOW" ou "MARKET" → prix d'entrée immédiate
            5. Gestion spéciale :
            - Si TP3 = "open" → marquer comme "open"
            - Détecter plusieurs prix d'entrée pour le canal 2

            ## Exemples de sortie :

            ### Canal 1 (3 TPs) :
            {{
            "symbol": "XAUUSD",
            "sens": "BUY",
            "entry_price": 2329.79,
            "sl": 2314.90,
            "tps": [2350.00, 2375.00, 2403.50]
            }}

            ### Canal 2 (3 entrées) :
            {{
            "symbol": "EURUSD",
            "sens": "SELL",
            "entry_prices": [1.0850, 1.0860, 1.0870],
            "sl": 1.0900,
            "tps": []
            }}

            ## Message à analyser :
            \"\"\"
            {self.signal}
            \"\"\"

            ## Variantes acceptées :
            - Symboles : "BTC/USDT" → "BTCUSDT", "XAU/USD" → "XAUUSD"
            - Stop loss : "SL", "stop", "stop-loss"
            - Take profit : "TP", "target", "take-profit"
            - Entrée : "Entry", "Buy at", "Sell at", "NOW", "@"

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
            print(f"Erreur ChatGPT: {e}")
            return None
    
    @staticmethod
    def signal_cleaner(response):
        try:
            # Extraire le JSON de la réponse
            content = response.choices[0].message.content
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                signal = json.loads(match.group(0))
                return signal
            return None
        except Exception as e:
            print(f"Erreur lors du nettoyage du signal: {e}")
            return None