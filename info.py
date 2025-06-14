# Configuration des instruments de trading

class Infos:
    """
    Classe contenant les informations sur les instruments de trading.
    """
    
    # Dictionnaire des configurations d'instruments
    INSTRUMENTS_CONFIG = {
        'EURUSD': {
            'pip_size': 0.0001,
            'pip_value_per_lot_eur': 10.0,  # Valeur approximative d'un pip pour 1 lot en EUR
            'min_lot': 0.01,
            'max_lot': 100.0
        },
        'GBPUSD': {
            'pip_size': 0.0001,
            'pip_value_per_lot_eur': 12.0,  # Valeur approximative
            'min_lot': 0.01,
            'max_lot': 100.0
        },
        'USDJPY': {
            'pip_size': 0.01,
            'pip_value_per_lot_eur': 8.5,   # Valeur approximative
            'min_lot': 0.01,
            'max_lot': 100.0
        },
        'XAUUSD': {  # Or
            'pip_size': 0.01,
            'pip_value_per_lot_eur': 10.0,  # Valeur approximative
            'min_lot': 0.01,
            'max_lot': 50.0
        },
        'BTCUSD': {
            'pip_size': 1.0,
            'pip_value_per_lot_eur': 0.001, # Valeur approximative
            'min_lot': 0.01,
            'max_lot': 10.0
        },
        'BTCUSDT': {
            'pip_size': 1.0,
            'pip_value_per_lot_eur': 0.001, # Valeur approximative
            'min_lot': 0.01,
            'max_lot': 10.0
        },
        'ETHUSDT': {
            'pip_size': 0.01,
            'pip_value_per_lot_eur': 0.01,  # Valeur approximative
            'min_lot': 0.01,
            'max_lot': 10.0
        }
    }
    
    @classmethod
    def get_instrument_info(cls, symbol):
        """
        Retourne les informations d'un instrument.
        
        Args:
            symbol (str): Symbole de l'instrument
        
        Returns:
            dict: Informations de l'instrument ou None si non trouvé
        """
        return cls.INSTRUMENTS_CONFIG.get(symbol.upper())
    
    @classmethod
    def get_pip_size(cls, symbol):
        """
        Retourne la taille d'un pip pour un instrument.
        
        Args:
            symbol (str): Symbole de l'instrument
        
        Returns:
            float: Taille du pip ou None si instrument non trouvé
        """
        info = cls.get_instrument_info(symbol)
        return info['pip_size'] if info else None
    
    @classmethod
    def get_pip_value(cls, symbol):
        """
        Retourne la valeur d'un pip en EUR pour un lot standard.
        
        Args:
            symbol (str): Symbole de l'instrument
        
        Returns:
            float: Valeur du pip en EUR ou None si instrument non trouvé
        """
        info = cls.get_instrument_info(symbol)
        return info['pip_value_per_lot_eur'] if info else None
    
    @classmethod
    def get_lot_limits(cls, symbol):
        """
        Retourne les limites de lot pour un instrument.
        
        Args:
            symbol (str): Symbole de l'instrument
        
        Returns:
            tuple: (min_lot, max_lot) ou (None, None) si instrument non trouvé
        """
        info = cls.get_instrument_info(symbol)
        if info:
            return info['min_lot'], info['max_lot']
        return None, None