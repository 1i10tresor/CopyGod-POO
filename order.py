import MetaTrader5 as mt5
from datetime import datetime
import time
from config import trading_config

class SendOrder:
    def __init__(self):
        """
        Initialise la classe SendOrder pour la gestion des ordres MT5.
        """
        self.orders_history = []
        self.is_connected = False
        self.expected_demo_login = None
        self._initialize_mt5()
    
    def _initialize_mt5(self):
        """
        Initialise la connexion à MetaTrader 5 avec le compte démo spécifique.
        Force la connexion au bon compte démo et vérifie avant toute opération.
        """
        try:
            print("🔄 Initialisation de MetaTrader 5...")
            
            # Initialiser MT5
            if not mt5.initialize():
                print(f"❌ Erreur d'initialisation MT5: {mt5.last_error()}")
                return False
            
            # Récupérer les identifiants du compte démo depuis la configuration
            credentials = trading_config.get_mt5_credentials()
            
            if not credentials['login'] or not credentials['password'] or not credentials['server']:
                print("❌ Identifiants MT5 manquants dans la configuration")
                print("💡 Vérifiez vos variables MT5_DEMO_LOGIN, MT5_DEMO_MDP, MT5_DEMO_SERVEUR dans .env")
                mt5.shutdown()
                return False
            
            # Convertir le login en entier si c'est une chaîne
            try:
                self.expected_demo_login = int(credentials['login'])
            except ValueError:
                print(f"❌ Login MT5 invalide: {credentials['login']}")
                mt5.shutdown()
                return False
            
            print(f"🎯 Connexion FORCÉE au compte démo MT5...")
            print(f"   Login attendu: {self.expected_demo_login}")
            print(f"   Serveur: {credentials['server']}")
            
            # Vérifier d'abord si on est déjà connecté au bon compte
            current_account = mt5.account_info()
            if current_account and current_account.login == self.expected_demo_login:
                print(f"✅ Déjà connecté au bon compte démo: {current_account.login}")
                if current_account.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
                    self.is_connected = True
                    self._display_account_info(current_account)
                    return True
                else:
                    print("⚠️  ATTENTION: Ce compte n'est pas en mode démo!")
            
            # Se connecter au compte spécifique
            print(f"🔄 Connexion au compte démo {self.expected_demo_login}...")
            authorized = mt5.login(
                login=self.expected_demo_login,
                password=credentials['password'],
                server=credentials['server']
            )
            
            if not authorized:
                error = mt5.last_error()
                print(f"❌ Échec de la connexion au compte démo: {error}")
                print("💡 Vérifiez vos identifiants MT5 dans le fichier .env")
                print("💡 Assurez-vous que MetaTrader 5 est ouvert")
                mt5.shutdown()
                return False
            
            # Vérifier que nous sommes bien connectés au bon compte
            account_info = mt5.account_info()
            if not account_info:
                print("❌ Impossible d'obtenir les informations du compte après connexion")
                mt5.shutdown()
                return False
            
            # Vérification stricte du compte
            if account_info.login != self.expected_demo_login:
                print(f"❌ ERREUR: Connecté au mauvais compte!")
                print(f"   Attendu: {self.expected_demo_login}")
                print(f"   Obtenu: {account_info.login}")
                mt5.shutdown()
                return False
            
            # Vérifier que c'est bien un compte démo
            if account_info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
                print("🚨 ALERTE SÉCURITÉ: Ce n'est pas un compte démo!")
                print(f"   Mode de trading: {account_info.trade_mode}")
                print("🛑 CONNEXION REFUSÉE pour votre sécurité")
                mt5.shutdown()
                return False
            
            self.is_connected = True
            print("✅ Connexion MT5 établie avec succès au compte démo")
            self._display_account_info(account_info)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation MT5: {e}")
            if mt5.initialize():
                mt5.shutdown()
            return False
    
    def _display_account_info(self, account_info):
        """
        Affiche les informations du compte de manière formatée.
        """
        print("\n" + "=" * 60)
        print("INFORMATIONS DU COMPTE MT5")
        print("=" * 60)
        print(f"Login: {account_info.login}")
        print(f"Nom: {account_info.name}")
        print(f"Serveur: {account_info.server}")
        print(f"Balance: {account_info.balance:.2f} {account_info.currency}")
        print(f"Equity: {account_info.equity:.2f} {account_info.currency}")
        print(f"Marge libre: {account_info.margin_free:.2f} {account_info.currency}")
        
        # Affichage du mode avec couleurs
        if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
            print(f"Mode: 🟢 DÉMO (Sécurisé)")
        else:
            print(f"Mode: 🔴 RÉEL (Attention!)")
        
        print("=" * 60 + "\n")
    
    def verify_demo_connection(self):
        """
        Vérifie que nous sommes bien connectés au bon compte démo.
        Cette vérification est effectuée avant chaque opération critique.
        
        Returns:
            bool: True si connecté au bon compte démo
        """
        if not self.is_connected:
            print("❌ MT5 n'est pas connecté")
            return False
        
        try:
            account_info = mt5.account_info()
            if not account_info:
                print("❌ Impossible d'obtenir les informations du compte")
                return False
            
            # Vérifier le login
            if account_info.login != self.expected_demo_login:
                print(f"🚨 ALERTE: Connecté au mauvais compte!")
                print(f"   Attendu: {self.expected_demo_login}")
                print(f"   Actuel: {account_info.login}")
                return False
            
            # Vérifier que c'est un compte démo
            if account_info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
                print(f"🚨 ALERTE SÉCURITÉ: Ce n'est pas un compte démo!")
                print(f"   Mode actuel: {account_info.trade_mode}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du compte: {e}")
            return False
    
    def force_reconnect_to_demo(self):
        """
        Force la reconnexion au compte démo spécifique.
        """
        print("🔄 Reconnexion forcée au compte démo...")
        
        # Fermer la connexion actuelle
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            time.sleep(1)  # Petite pause pour s'assurer que la déconnexion est complète
        
        # Réinitialiser
        success = self._initialize_mt5()
        if success:
            print("✅ Reconnexion au compte démo réussie")
        else:
            print("❌ Échec de la reconnexion au compte démo")
        
        return success
    
    def _ensure_demo_connection(self):
        """
        S'assure que nous sommes connectés au bon compte démo.
        Tente une reconnexion si nécessaire.
        
        Returns:
            bool: True si la connexion au compte démo est confirmée
        """
        # Première vérification
        if self.verify_demo_connection():
            return True
        
        print("⚠️  Connexion au compte démo invalide, tentative de reconnexion...")
        
        # Tentative de reconnexion
        if self.force_reconnect_to_demo():
            # Vérification finale
            if self.verify_demo_connection():
                return True
        
        print("❌ Impossible de se connecter au compte démo")
        print("🛑 Opération annulée pour votre sécurité")
        return False
    
    def _get_symbol_trading_info(self, symbol):
        """
        Récupère les informations de trading détaillées pour un symbole.
        
        Args:
            symbol (str): Symbole à analyser
        
        Returns:
            dict: Informations détaillées ou None
        """
        try:
            # Sélectionner le symbole
            if not mt5.symbol_select(symbol, True):
                print(f"❌ Impossible de sélectionner {symbol}")
                return None
            
            # Obtenir les informations
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                print(f"❌ Impossible d'obtenir les infos pour {symbol}")
                return None
            
            # Obtenir le tick actuel
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                print(f"❌ Impossible d'obtenir le tick pour {symbol}")
                return None
            
            return {
                'symbol': symbol,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'tick_size': symbol_info.trade_tick_size,
                'tick_value': symbol_info.trade_tick_value,
                'min_lot': symbol_info.volume_min,
                'max_lot': symbol_info.volume_max,
                'lot_step': symbol_info.volume_step,
                'stops_level': symbol_info.trade_stops_level,
                'freeze_level': symbol_info.trade_freeze_level,
                'current_bid': tick.bid,
                'current_ask': tick.ask,
                'spread': tick.ask - tick.bid,
                'trade_mode': symbol_info.trade_mode,
                'filling_mode': symbol_info.filling_mode
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos pour {symbol}: {e}")
            return None
    
    def _validate_order_request(self, request, symbol_info_dict):
        """
        Valide une requête d'ordre avant envoi et suggère des corrections.
        
        Args:
            request (dict): Requête d'ordre MT5
            symbol_info_dict (dict): Informations du symbole
        
        Returns:
            tuple: (request_corrigée, est_valide, messages_diagnostic)
        """
        diagnostics = []
        corrected_request = request.copy()
        is_valid = True
        
        try:
            symbol = request['symbol']
            order_type = request['type']
            price = request['price']
            sl = request.get('sl', 0)
            tp = request.get('tp', 0)
            volume = request['volume']
            
            # Vérifier le volume
            min_lot = symbol_info_dict['min_lot']
            max_lot = symbol_info_dict['max_lot']
            lot_step = symbol_info_dict['lot_step']
            
            if volume < min_lot:
                diagnostics.append(f"⚠️  Volume {volume} < minimum {min_lot}")
                corrected_request['volume'] = min_lot
            elif volume > max_lot:
                diagnostics.append(f"⚠️  Volume {volume} > maximum {max_lot}")
                corrected_request['volume'] = max_lot
                
            # Vérifier que le volume respecte le step
            volume_steps = round(volume / lot_step)
            corrected_volume = volume_steps * lot_step
            if abs(corrected_volume - volume) > 0.0001:
                diagnostics.append(f"💡 Volume ajusté de {volume} à {corrected_volume} (step: {lot_step})")
                corrected_request['volume'] = corrected_volume
            
            # Normaliser les prix selon la précision
            digits = symbol_info_dict['digits']
            point = symbol_info_dict['point']
            
            price_normalized = round(price, digits)
            if abs(price_normalized - price) > point/2:
                diagnostics.append(f"💡 Prix normalisé de {price} à {price_normalized}")
                corrected_request['price'] = price_normalized
            
            if sl > 0:
                sl_normalized = round(sl, digits)
                if abs(sl_normalized - sl) > point/2:
                    diagnostics.append(f"💡 SL normalisé de {sl} à {sl_normalized}")
                    corrected_request['sl'] = sl_normalized
            
            if tp > 0:
                tp_normalized = round(tp, digits)
                if abs(tp_normalized - tp) > point/2:
                    diagnostics.append(f"💡 TP normalisé de {tp} à {tp_normalized}")
                    corrected_request['tp'] = tp_normalized
            
            # Vérifier les distances minimales pour les ordres en attente
            if request['action'] == mt5.TRADE_ACTION_PENDING:
                stops_level = symbol_info_dict['stops_level']
                freeze_level = symbol_info_dict['freeze_level']
                current_bid = symbol_info_dict['current_bid']
                current_ask = symbol_info_dict['current_ask']
                
                diagnostics.append(f"📊 Stops level: {stops_level} points")
                diagnostics.append(f"📊 Freeze level: {freeze_level} points")
                
                # Calculer les distances minimales
                min_distance = max(stops_level, freeze_level) * point
                
                if order_type in [mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP]:
                    current_price = current_ask
                    if order_type == mt5.ORDER_TYPE_BUY_LIMIT:
                        # BUY LIMIT doit être en dessous du prix actuel
                        if price >= current_price:
                            diagnostics.append(f"❌ BUY LIMIT: prix {price} doit être < prix actuel {current_price}")
                            is_valid = False
                        else:
                            distance = current_price - price
                            if distance < min_distance:
                                diagnostics.append(f"❌ BUY LIMIT: distance {distance:.5f} < minimum {min_distance:.5f}")
                                suggested_price = current_price - min_distance
                                diagnostics.append(f"💡 Prix suggéré: {suggested_price:.5f}")
                                is_valid = False
                    else:  # BUY STOP
                        # BUY STOP doit être au dessus du prix actuel
                        if price <= current_price:
                            diagnostics.append(f"❌ BUY STOP: prix {price} doit être > prix actuel {current_price}")
                            is_valid = False
                        else:
                            distance = price - current_price
                            if distance < min_distance:
                                diagnostics.append(f"❌ BUY STOP: distance {distance:.5f} < minimum {min_distance:.5f}")
                                suggested_price = current_price + min_distance
                                diagnostics.append(f"💡 Prix suggéré: {suggested_price:.5f}")
                                is_valid = False
                
                elif order_type in [mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP]:
                    current_price = current_bid
                    if order_type == mt5.ORDER_TYPE_SELL_LIMIT:
                        # SELL LIMIT doit être au dessus du prix actuel
                        if price <= current_price:
                            diagnostics.append(f"❌ SELL LIMIT: prix {price} doit être > prix actuel {current_price}")
                            is_valid = False
                        else:
                            distance = price - current_price
                            if distance < min_distance:
                                diagnostics.append(f"❌ SELL LIMIT: distance {distance:.5f} < minimum {min_distance:.5f}")
                                suggested_price = current_price + min_distance
                                diagnostics.append(f"💡 Prix suggéré: {suggested_price:.5f}")
                                is_valid = False
                    else:  # SELL STOP
                        # SELL STOP doit être en dessous du prix actuel
                        if price >= current_price:
                            diagnostics.append(f"❌ SELL STOP: prix {price} doit être < prix actuel {current_price}")
                            is_valid = False
                        else:
                            distance = current_price - price
                            if distance < min_distance:
                                diagnostics.append(f"❌ SELL STOP: distance {distance:.5f} < minimum {min_distance:.5f}")
                                suggested_price = current_price - min_distance
                                diagnostics.append(f"💡 Prix suggéré: {suggested_price:.5f}")
                                is_valid = False
            
            # Vérifier les modes de remplissage supportés
            filling_mode = symbol_info_dict['filling_mode']
            requested_filling = request.get('type_filling', mt5.ORDER_FILLING_IOC)
            
            # Vérifier si le mode de remplissage est supporté
            if filling_mode & requested_filling == 0:
                diagnostics.append(f"⚠️  Mode de remplissage {requested_filling} non supporté")
                # Essayer d'autres modes
                if filling_mode & mt5.ORDER_FILLING_FOK:
                    corrected_request['type_filling'] = mt5.ORDER_FILLING_FOK
                    diagnostics.append(f"💡 Utilisation de ORDER_FILLING_FOK")
                elif filling_mode & mt5.ORDER_FILLING_IOC:
                    corrected_request['type_filling'] = mt5.ORDER_FILLING_IOC
                    diagnostics.append(f"💡 Utilisation de ORDER_FILLING_IOC")
                elif filling_mode & mt5.ORDER_FILLING_RETURN:
                    corrected_request['type_filling'] = mt5.ORDER_FILLING_RETURN
                    diagnostics.append(f"💡 Utilisation de ORDER_FILLING_RETURN")
            
        except Exception as e:
            diagnostics.append(f"❌ Erreur lors de la validation: {e}")
            is_valid = False
        
        return corrected_request, is_valid, diagnostics
    
    def place_signal_orders(self, signals, lot_sizes, channel_id=1):
        """
        Place tous les ordres pour un signal complet.
        VÉRIFICATION OBLIGATOIRE du compte démo avant placement.
        
        Args:
            signals: Signal(s) à traiter
            lot_sizes (list): Tailles de lot pour chaque ordre
            channel_id (int): ID du canal
        
        Returns:
            list: Liste des résultats d'ordres
        """
        print("🔍 Vérification de la connexion au compte démo avant placement d'ordres...")
        
        # VÉRIFICATION OBLIGATOIRE du compte démo
        if not self._ensure_demo_connection():
            print("🚫 PLACEMENT D'ORDRES ANNULÉ - Connexion au compte démo non confirmée")
            return []
        
        print("✅ Connexion au compte démo confirmée, placement des ordres autorisé")
        
        if channel_id == 1:
            return self._place_channel_1_orders(signals, lot_sizes)
        elif channel_id == 2:
            return self._place_channel_2_orders(signals, lot_sizes)
        else:
            print(f"Canal {channel_id} non supporté")
            return []
    
    def _place_channel_1_orders(self, signal, lot_sizes):
        """
        Place 3 ordres pour le canal 1 (même entrée, 3 TPs différents).
        """
        if not self.is_connected:
            print("❌ MT5 n'est pas connecté")
            return []
        
        results = []
        symbol = signal['symbol']
        entry_price = signal['entry_price']
        sl_price = signal['sl']
        tps = signal['tps']
        sens = signal['sens']
        
        try:
            # Obtenir les informations détaillées du symbole
            symbol_info_dict = self._get_symbol_trading_info(symbol)
            if not symbol_info_dict:
                return []
            
            print(f"📊 Informations {symbol}:")
            print(f"   Digits: {symbol_info_dict['digits']}, Point: {symbol_info_dict['point']}")
            print(f"   Stops level: {symbol_info_dict['stops_level']} points")
            print(f"   Freeze level: {symbol_info_dict['freeze_level']} points")
            print(f"   Prix actuel: Bid={symbol_info_dict['current_bid']}, Ask={symbol_info_dict['current_ask']}")
            
            current_price = symbol_info_dict['current_ask'] if sens == 'BUY' else symbol_info_dict['current_bid']
            print(f"💰 Prix de référence pour {sens}: {current_price}")
            print(f"🎯 Prix d'entrée souhaité: {entry_price}")
            
            print(f"📈 Placement de 3 ordres pour {symbol} {sens} (Canal 1)")
            
            # Placer un ordre pour chaque TP
            for i in range(3):
                if i >= len(lot_sizes) or i >= len(tps):
                    break
                
                lot_size = lot_sizes[i]
                tp_price = tps[i]
                
                print(f"\n🔍 Ordre TP{i+1}: {lot_size} lots → TP {tp_price}")
                
                # Déterminer le type d'ordre selon les prix
                if abs(entry_price - current_price) <= 5 * symbol_info_dict['point']:
                    # Prix très proche, ordre au marché
                    order_type = mt5.ORDER_TYPE_BUY if sens == 'BUY' else mt5.ORDER_TYPE_SELL
                    action = mt5.TRADE_ACTION_DEAL
                    execution_price = current_price
                    order_type_name = f"{sens} (Marché)"
                else:
                    # Ordre en attente
                    if sens == 'BUY':
                        if entry_price < current_price:
                            order_type = mt5.ORDER_TYPE_BUY_LIMIT
                            order_type_name = "BUY LIMIT"
                        else:
                            order_type = mt5.ORDER_TYPE_BUY_STOP
                            order_type_name = "BUY STOP"
                    else:  # SELL
                        if entry_price > current_price:
                            order_type = mt5.ORDER_TYPE_SELL_LIMIT
                            order_type_name = "SELL LIMIT"
                        else:
                            order_type = mt5.ORDER_TYPE_SELL_STOP
                            order_type_name = "SELL STOP"
                    
                    action = mt5.TRADE_ACTION_PENDING
                    execution_price = entry_price
                
                print(f"📋 Type d'ordre: {order_type_name}")
                print(f"💲 Prix d'exécution: {execution_price}")
                
                # Préparer la requête
                request = {
                    "action": action,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": order_type,
                    "price": execution_price,
                    "sl": sl_price,
                    "tp": tp_price,
                    "deviation": trading_config.MT5_DEVIATION,
                    "magic": trading_config.MT5_MAGIC_BASE + i,
                    "comment": f"Signal Canal 1 - TP{i+1} - DEMO",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                # Valider et corriger la requête
                corrected_request, is_valid, diagnostics = self._validate_order_request(request, symbol_info_dict)
                
                print(f"🔍 Diagnostic de l'ordre TP{i+1}:")
                for diag in diagnostics:
                    print(f"   {diag}")
                
                if not is_valid:
                    print(f"❌ Ordre TP{i+1} invalide, passage ignoré")
                    continue
                
                print(f"📋 Requête finale: {corrected_request}")
                
                # Envoyer l'ordre
                result = mt5.order_send(corrected_request)
                
                # Diagnostic détaillé du résultat
                if result is None:
                    error = mt5.last_error()
                    print(f"❌ Ordre TP{i+1} - Résultat None. Erreur MT5: {error}")
                    continue
                
                print(f"📊 Résultat ordre TP{i+1}: retcode={result.retcode}, comment='{result.comment}'")
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"❌ Erreur ordre TP{i+1}: {result.retcode} - {result.comment}")
                    print(f"   Détails complets: {result}")
                    continue
                
                # Créer les détails de l'ordre
                order_details = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'type': sens,
                    'entry_price': execution_price,
                    'lot_size': corrected_request['volume'],
                    'stop_loss': corrected_request['sl'],
                    'take_profit': corrected_request['tp'],
                    'tp_number': i + 1,
                    'status': 'FILLED' if action == mt5.TRADE_ACTION_DEAL else 'PENDING',
                    'order_type': order_type_name,
                    'mt5_order_id': result.order,
                    'mt5_deal_id': result.deal if hasattr(result, 'deal') else None,
                    'channel_id': 1,
                    'account_type': 'DEMO'
                }
                
                results.append(order_details)
                self.orders_history.append(order_details)
                
                print(f"✅ Ordre TP{i+1} placé: {corrected_request['volume']} lots à {execution_price} → TP {corrected_request['tp']}")
                time.sleep(0.1)  # Petite pause entre les ordres
            
            if results:
                self._display_signal_orders(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors du placement des ordres canal 1: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _place_channel_2_orders(self, signals, lot_sizes):
        """
        Place 3 ordres pour le canal 2 (3 entrées différentes, RR fixe).
        """
        if not self.is_connected:
            print("❌ MT5 n'est pas connecté")
            return []
        
        results = []
        
        try:
            print(f"📈 Placement de {len(signals)} ordres (Canal 2)")
            
            for i, (signal, lot_size) in enumerate(zip(signals, lot_sizes)):
                symbol = signal['symbol']
                entry_price = signal['entry_price']
                sl_price = signal['sl']
                tp_price = signal['tps'][0]  # Un seul TP par ordre
                sens = signal['sens']
                rr_ratio = signal['rr_ratio']
                
                print(f"\n🔍 Traitement ordre {i+1}: {symbol} {sens}")
                print(f"   Entrée: {entry_price}, SL: {sl_price}, TP: {tp_price}")
                
                # Obtenir les informations détaillées du symbole
                symbol_info_dict = self._get_symbol_trading_info(symbol)
                if not symbol_info_dict:
                    continue
                
                print(f"📊 Info symbole: digits={symbol_info_dict['digits']}, point={symbol_info_dict['point']}")
                print(f"   Stops level: {symbol_info_dict['stops_level']} points")
                print(f"   Freeze level: {symbol_info_dict['freeze_level']} points")
                
                current_price = symbol_info_dict['current_ask'] if sens == 'BUY' else symbol_info_dict['current_bid']
                print(f"💰 Prix de référence pour {sens}: {current_price}")
                print(f"🎯 Prix d'entrée souhaité: {entry_price}")
                
                # Déterminer le type d'ordre selon les prix
                if abs(entry_price - current_price) <= 5 * symbol_info_dict['point']:
                    # Prix très proche, ordre au marché
                    order_type = mt5.ORDER_TYPE_BUY if sens == 'BUY' else mt5.ORDER_TYPE_SELL
                    action = mt5.TRADE_ACTION_DEAL
                    execution_price = current_price
                    order_type_name = f"{sens} (Marché)"
                else:
                    # Ordre en attente
                    if sens == 'BUY':
                        if entry_price < current_price:
                            order_type = mt5.ORDER_TYPE_BUY_LIMIT
                            order_type_name = "BUY LIMIT"
                        else:
                            order_type = mt5.ORDER_TYPE_BUY_STOP
                            order_type_name = "BUY STOP"
                    else:  # SELL
                        if entry_price > current_price:
                            order_type = mt5.ORDER_TYPE_SELL_LIMIT
                            order_type_name = "SELL LIMIT"
                        else:
                            order_type = mt5.ORDER_TYPE_SELL_STOP
                            order_type_name = "SELL STOP"
                    
                    action = mt5.TRADE_ACTION_PENDING
                    execution_price = entry_price
                
                print(f"📋 Type d'ordre: {order_type_name}")
                print(f"💲 Prix d'exécution: {execution_price}")
                
                # Préparer la requête
                request = {
                    "action": action,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": order_type,
                    "price": execution_price,
                    "sl": sl_price,
                    "tp": tp_price,
                    "deviation": trading_config.MT5_DEVIATION,
                    "magic": trading_config.MT5_MAGIC_BASE + 1000 + i,
                    "comment": f"Signal Canal 2 - RR{rr_ratio} - DEMO",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                # Valider et corriger la requête
                corrected_request, is_valid, diagnostics = self._validate_order_request(request, symbol_info_dict)
                
                print(f"🔍 Diagnostic de l'ordre RR{rr_ratio}:")
                for diag in diagnostics:
                    print(f"   {diag}")
                
                if not is_valid:
                    print(f"❌ Ordre RR{rr_ratio} invalide, passage ignoré")
                    continue
                
                print(f"📋 Requête finale: {corrected_request}")
                
                # Envoyer l'ordre
                result = mt5.order_send(corrected_request)
                
                # Diagnostic détaillé du résultat
                if result is None:
                    error = mt5.last_error()
                    print(f"❌ Ordre {i+1} - Résultat None. Erreur MT5: {error}")
                    continue
                
                print(f"📊 Résultat ordre RR{rr_ratio}: retcode={result.retcode}, comment='{result.comment}'")
                
                # Vérifier le code de retour
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"❌ Erreur ordre RR{rr_ratio}: {result.retcode} - {result.comment}")
                    print(f"   Détails complets: {result}")
                    continue
                
                # Créer les détails de l'ordre
                order_details = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'type': sens,
                    'entry_price': execution_price,
                    'lot_size': corrected_request['volume'],
                    'stop_loss': corrected_request['sl'],
                    'take_profit': corrected_request['tp'],
                    'rr_ratio': rr_ratio,
                    'order_index': i + 1,
                    'status': 'FILLED' if action == mt5.TRADE_ACTION_DEAL else 'PENDING',
                    'order_type': order_type_name,
                    'mt5_order_id': result.order,
                    'mt5_deal_id': result.deal if hasattr(result, 'deal') else None,
                    'channel_id': 2,
                    'account_type': 'DEMO'
                }
                
                results.append(order_details)
                self.orders_history.append(order_details)
                
                print(f"✅ Ordre RR{rr_ratio} placé: {corrected_request['volume']} lots, {order_type_name} à {execution_price} → TP {corrected_request['tp']}")
                time.sleep(0.1)
            
            if results:
                self._display_signal_orders(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors du placement des ordres canal 2: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _display_signal_orders(self, orders):
        """
        Affiche les détails des ordres d'un signal.
        """
        if not orders:
            return
        
        print("\n" + "=" * 70)
        print(f"SIGNAL TRAITÉ - CANAL {orders[0]['channel_id']} - {len(orders)} ORDRES PLACÉS")
        print(f"COMPTE: 🟢 {orders[0]['account_type']}")
        print("=" * 70)
        print(f"Symbole: {orders[0]['symbol']}")
        print(f"Direction: {orders[0]['type']}")
        print(f"Stop Loss: {orders[0]['stop_loss']}")
        print("-" * 70)
        
        for i, order in enumerate(orders, 1):
            if order['channel_id'] == 1:
                print(f"Ordre {i} - TP{order['tp_number']}: {order['lot_size']} lots → {order['take_profit']}")
            else:
                print(f"Ordre {i} - RR{order['rr_ratio']}: {order['lot_size']} lots → {order['take_profit']}")
            print(f"  Type: {order.get('order_type', 'N/A')} | Prix: {order['entry_price']}")
            print(f"  ID MT5: {order['mt5_order_id']} | Statut: {order['status']}")
        
        print("=" * 70 + "\n")
    
    def get_account_info(self):
        """
        Retourne les informations du compte MT5.
        Vérifie d'abord que nous sommes connectés au bon compte démo.
        """
        if not self.verify_demo_connection():
            print("⚠️  Connexion au compte démo non confirmée")
            return None
        
        try:
            account_info = mt5.account_info()
            if account_info:
                return {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'free_margin': account_info.margin_free,
                    'currency': account_info.currency,
                    'name': account_info.name,
                    'server': account_info.server,
                    'trade_mode': account_info.trade_mode,
                    'is_demo': account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO
                }
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des informations du compte: {e}")
            return None
    
    def get_open_positions(self):
        """
        Retourne les positions ouvertes.
        Vérifie d'abord la connexion au compte démo.
        """
        if not self.verify_demo_connection():
            print("⚠️  Connexion au compte démo non confirmée")
            return []
        
        try:
            positions = mt5.positions_get()
            return list(positions) if positions else []
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des positions: {e}")
            return []
    
    def get_orders_history(self):
        """
        Retourne l'historique des ordres.
        """
        return self.orders_history
    
    def close_connection(self):
        """
        Ferme la connexion MT5.
        """
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            print("🔴 Connexion MT5 fermée")