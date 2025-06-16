from openai import OpenAI
import dotenv
import os
import re
import json

class chatGpt():
    def __init__(self, signal, channel_id=1):
        dotenv.load_dotenv()
        self.gpt_key = os.getenv("GPT_KEY")
        self.signal = signal
        self.channel_id = channel_id
        
        # Initialiser le client OpenAI avec la nouvelle API
        self.client = OpenAI(api_key=self.gpt_key)
        
        self.prompt = f"""
            Analyse le message de trading suivant et extrais les informations essentielles au format JSON strict.
            
            CANAL SPÉCIFIÉ: {channel_id}

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

            ## GESTION SPÉCIALE CANAL 2 - FOURCHETTES ET SL ABRÉGÉS :
            
            ### Format fourchette (ex: "3349-52") :
            - "3349-52" signifie de 3349 à 3352
            - Générer 3 prix d'entrée : [prix_bas, prix_milieu, prix_haut]
            - Exemple : "3349-52" → [3349, 3350.5, 3352]
            
            ### SL abrégé (ex: "sl 54.5" quand prix = "3349-52") :
            - Prendre les chiffres avant le tiret comme base : "3349-52" → base = "33"
            - SL "54.5" → "3354.5"
            - Si SL < 100, ajouter les centaines de la base
            - Si SL ≥ 100, utiliser tel quel
            
            ### Exemples de transformation :
            
            #### Exemple 1 :
            Signal : "go sell 3349-52, tp 3330, sl 54.5"
            → entry_prices: [3349, 3350.5, 3352]
            → sl: 3354.5 (33 + 54.5)
            → tp: 3330
            
            #### Exemple 2 :
            Signal : "buy 1850-55, tp 1870, sl 45"
            → entry_prices: [1850, 1852.5, 1855]
            → sl: 1845 (18 + 45)
            → tp: 1870
            
            #### Exemple 3 :
            Signal : "sell 2100-10, tp 2080, sl 115"
            → entry_prices: [2100, 2105, 2110]
            → sl: 2115 (utiliser tel quel car ≥ 100)
            → tp: 2080

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

            ### Canal 2 (3 entrées avec fourchette) :
            {{
            "symbol": "XAUUSD",
            "sens": "SELL",
            "entry_prices": [3349, 3350.5, 3352],
            "sl": 3354.5,
            "tps": [3330]
            }}

            ### Canal 2 (3 entrées normales) :
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
            - Fourchettes : "3349-52", "1850-55", "2100-10"

            Résultat JSON :
            """

    def get_signal(self):
        try:
            # Utiliser la nouvelle API OpenAI v1.0+
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
            # Extraire le JSON de la réponse avec la nouvelle structure
            content = response.choices[0].message.content
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                signal = json.loads(match.group(0))
                return signal
            return None
        except Exception as e:
            print(f"Erreur lors du nettoyage du signal: {e}")
            return None