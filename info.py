import MetaTrader5 as mt5

class Infos:
    """
    Classe pour récupérer les informations des instruments via l'API MT5.
    """
    
    @staticmethod
    def get_symbol_info(symbol):
        """
        Récupère les informations d'un symbole via MT5.
        
        Args:
            symbol (str): Symbole de l'instrument
        
        Returns:
            dict: Informations du symbole ou None si erreur
        """
        try:
            # Sélectionner le symbole
            if not mt5.symbol_select(symbol, True):
                print(f"Impossible de sélectionner le symbole {symbol}")
                return None
            
            # Obtenir les informations du symbole
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                print(f"Impossible d'obtenir les informations pour {symbol}")
                return None
            
            return {
                'symbol': symbol,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'pip_size': symbol_info.point * (10 if symbol_info.digits == 5 or symbol_info.digits == 3 else 1),
                'tick_size': symbol_info.trade_tick_size,
                'tick_value': symbol_info.trade_tick_value,
                'contract_size': symbol_info.trade_contract_size,
                'min_lot': symbol_info.volume_min,
                'max_lot': symbol_info.volume_max,
                'lot_step': symbol_info.volume_step,
                'currency_base': symbol_info.currency_base,
                'currency_profit': symbol_info.currency_profit,
                'currency_margin': symbol_info.currency_margin
            }
            
        except Exception as e:
            print(f"Erreur lors de la récupération des informations du symbole {symbol}: {e}")
            return None
    
    @staticmethod
    def get_pip_value_eur(symbol, lot_size=1.0):
        """
        Calcule la valeur d'un pip en EUR pour une taille de lot donnée.
        
        Args:
            symbol (str): Symbole de l'instrument
            lot_size (float): Taille du lot
        
        Returns:
            float: Valeur du pip en EUR ou None si erreur
        """
        try:
            symbol_info = Infos.get_symbol_info(symbol)
            if not symbol_info:
                return None
            
            # Valeur du tick en devise de profit
            tick_value = symbol_info['tick_value']
            tick_size = symbol_info['tick_size']
            pip_size = symbol_info['pip_size']
            
            # Calculer la valeur du pip
            pip_value = (tick_value / tick_size) * pip_size * lot_size
            
            # Convertir en EUR si nécessaire
            profit_currency = symbol_info['currency_profit']
            if profit_currency != 'EUR':
                # Obtenir le taux de change vers EUR
                conversion_rate = Infos._get_conversion_rate_to_eur(profit_currency)
                if conversion_rate:
                    pip_value *= conversion_rate
            
            return pip_value
            
        except Exception as e:
            print(f"Erreur lors du calcul de la valeur du pip pour {symbol}: {e}")
            return None
    
    @staticmethod
    def _get_conversion_rate_to_eur(currency):
        """
        Obtient le taux de conversion d'une devise vers EUR.
        
        Args:
            currency (str): Devise à convertir
        
        Returns:
            float: Taux de conversion ou 1.0 si EUR ou erreur
        """
        if currency == 'EUR':
            return 1.0
        
        try:
            # Essayer d'abord CURRENCY/EUR
            symbol = f"{currency}EUR"
            if mt5.symbol_select(symbol, True):
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    return tick.bid
            
            # Essayer EUR/CURRENCY et inverser
            symbol = f"EUR{currency}"
            if mt5.symbol_select(symbol, True):
                tick = mt5.symbol_info_tick(symbol)
                if tick and tick.bid > 0:
                    return 1.0 / tick.bid
            
            # Si USD, essayer EURUSD
            if currency == 'USD':
                if mt5.symbol_select('EURUSD', True):
                    tick = mt5.symbol_info_tick('EURUSD')
                    if tick and tick.bid > 0:
                        return 1.0 / tick.bid
            
            print(f"Impossible de trouver le taux de conversion pour {currency}/EUR")
            return 1.0  # Valeur par défaut
            
        except Exception as e:
            print(f"Erreur lors de la conversion {currency}/EUR: {e}")
            return 1.0
    
    @staticmethod
    def calculate_points_distance(symbol, price1, price2):
        """
        Calcule la distance en points entre deux prix.
        
        Args:
            symbol (str): Symbole de l'instrument
            price1 (float): Premier prix
            price2 (float): Deuxième prix
        
        Returns:
            float: Distance en points
        """
        try:
            symbol_info = Infos.get_symbol_info(symbol)
            if not symbol_info:
                return 0
            
            point = symbol_info['point']
            return abs(price1 - price2) / point
            
        except Exception as e:
            print(f"Erreur lors du calcul de la distance en points: {e}")
            return 0