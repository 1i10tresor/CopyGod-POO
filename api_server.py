from flask import Flask, jsonify, request
from flask_cors import CORS
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
import os
from config import config

app = Flask(__name__)
CORS(app)

class TradingAPI:
    def __init__(self, account_type='DEMO'):
        self.account_type = account_type.upper()
        self.is_connected = False
        self.current_login = None
        self._connect_mt5()
    
    def _connect_mt5(self):
        """Connexion à MT5 sur le compte spécifié."""
        try:
            if not mt5.initialize():
                print(f"❌ Erreur MT5: {mt5.last_error()}")
                return False
            
            # Obtenir les identifiants du compte
            credentials = config.get_mt5_credentials(self.account_type)
            
            if not all([credentials['login'], credentials['password'], credentials['server']]):
                print(f"❌ Identifiants MT5 manquants pour le compte {self.account_type}")
                return False
            
            self.current_login = credentials['login']
            
            # Se connecter
            authorized = mt5.login(
                login=credentials['login'],
                password=credentials['password'],
                server=credentials['server']
            )
            
            if not authorized:
                print(f"❌ Échec connexion MT5 ({self.account_type}): {mt5.last_error()}")
                return False
            
            # Vérifier la connexion
            account_info = mt5.account_info()
            if not account_info or account_info.login != self.current_login:
                print(f"❌ Connexion au mauvais compte")
                return False
            
            self.is_connected = True
            account_type_str = "DÉMO" if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else "RÉEL"
            print(f"✅ API connectée à MT5 ({self.account_type}) - Compte {account_type_str}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion MT5: {e}")
            return False
    
    def get_account_info(self):
        """Récupère les infos du compte."""
        if not self.is_connected:
            return None
        
        try:
            account_info = mt5.account_info()
            if account_info:
                return {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'freeMargin': account_info.margin_free,
                    'currency': account_info.currency,
                    'accountType': self.account_type,
                    'isDemo': account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO
                }
        except Exception as e:
            print(f"❌ Erreur récupération compte: {e}")
        
        return None
    
    def get_open_orders(self):
        """Récupère les ordres ouverts."""
        if not self.is_connected:
            return []
        
        try:
            # Positions ouvertes
            positions = mt5.positions_get()
            orders = []
            
            if positions:
                for pos in positions:
                    orders.append({
                        'id': str(pos.ticket),
                        'channelId': self._extract_channel_from_comment(pos.comment),
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == 0 else 'SELL',
                        'volume': pos.volume,
                        'entryPrice': pos.price_open,
                        'sl': pos.sl,
                        'tp': pos.tp,
                        'status': 'OPEN',
                        'pnl': pos.profit,
                        'accountType': self.account_type,
                        'timestamp': datetime.fromtimestamp(pos.time).isoformat()
                    })
            
            # Ordres en attente
            pending_orders = mt5.orders_get()
            if pending_orders:
                for order in pending_orders:
                    orders.append({
                        'id': str(order.ticket),
                        'channelId': self._extract_channel_from_comment(order.comment),
                        'symbol': order.symbol,
                        'type': 'BUY' if order.type in [2, 4] else 'SELL',
                        'volume': order.volume_initial,
                        'entryPrice': order.price_open,
                        'sl': order.sl,
                        'tp': order.tp,
                        'status': 'PENDING',
                        'pnl': 0,
                        'accountType': self.account_type,
                        'timestamp': datetime.fromtimestamp(order.time_setup).isoformat()
                    })
            
            return orders
            
        except Exception as e:
            print(f"❌ Erreur récupération ordres: {e}")
            return []
    
    def get_history(self, days=7):
        """Récupère l'historique des trades."""
        if not self.is_connected:
            return []
        
        try:
            # Date de début
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            # Récupérer l'historique
            deals = mt5.history_deals_get(from_date, to_date)
            history = []
            
            if deals:
                # Grouper les deals par position
                positions = {}
                for deal in deals:
                    if deal.position_id not in positions:
                        positions[deal.position_id] = []
                    positions[deal.position_id].append(deal)
                
                # Traiter chaque position fermée
                for pos_id, pos_deals in positions.items():
                    if len(pos_deals) >= 2:  # Ouverture + fermeture
                        open_deal = min(pos_deals, key=lambda x: x.time)
                        close_deal = max(pos_deals, key=lambda x: x.time)
                        
                        if open_deal.entry == 0 and close_deal.entry == 1:  # Entrée puis sortie
                            duration = (close_deal.time - open_deal.time) // 60  # en minutes
                            
                            history.append({
                                'id': f'HIS{pos_id}',
                                'channelId': self._extract_channel_from_comment(open_deal.comment),
                                'symbol': open_deal.symbol,
                                'type': 'BUY' if open_deal.type == 0 else 'SELL',
                                'volume': open_deal.volume,
                                'entryPrice': open_deal.price,
                                'exitPrice': close_deal.price,
                                'pnl': close_deal.profit,
                                'duration': duration,
                                'accountType': self.account_type,
                                'closeTime': datetime.fromtimestamp(close_deal.time).isoformat()
                            })
            
            return sorted(history, key=lambda x: x['closeTime'], reverse=True)
            
        except Exception as e:
            print(f"❌ Erreur récupération historique: {e}")
            return []
    
    def get_statistics(self):
        """Calcule les statistiques."""
        try:
            history = self.get_history(30)  # 30 derniers jours
            
            if not history:
                return self._empty_stats()
            
            # Stats globales
            total_trades = len(history)
            winning_trades = len([t for t in history if t['pnl'] > 0])
            win_rate = round((winning_trades / total_trades) * 100) if total_trades > 0 else 0
            
            # Risk/Reward moyen (approximation)
            avg_rr = 2.0  # Valeur par défaut
            
            # Stats par canal
            channel1_trades = [t for t in history if t['channelId'] == 1]
            channel2_trades = [t for t in history if t['channelId'] == 2]
            
            # Stats par symbole
            symbols = {}
            for trade in history:
                symbol = trade['symbol']
                if symbol not in symbols:
                    symbols[symbol] = []
                symbols[symbol].append(trade)
            
            symbol_stats = []
            for symbol, trades in symbols.items():
                wins = len([t for t in trades if t['pnl'] > 0])
                symbol_win_rate = round((wins / len(trades)) * 100) if trades else 0
                total_pnl = sum(t['pnl'] for t in trades)
                
                symbol_stats.append({
                    'symbol': symbol,
                    'totalTrades': len(trades),
                    'winRate': symbol_win_rate,
                    'avgRR': 2.0,  # Approximation
                    'totalPnl': total_pnl
                })
            
            return {
                'global': {
                    'winRate': win_rate,
                    'avgRR': avg_rr,
                    'totalSignals': total_trades
                },
                'channels': {
                    'channel1': self._calculate_channel_stats(channel1_trades),
                    'channel2': self._calculate_channel_stats(channel2_trades)
                },
                'symbols': symbol_stats,
                'accountType': self.account_type
            }
            
        except Exception as e:
            print(f"❌ Erreur calcul statistiques: {e}")
            return self._empty_stats()
    
    def _calculate_channel_stats(self, trades):
        """Calcule les stats d'un canal."""
        if not trades:
            return {
                'totalSignals': 0,
                'winRate': 0,
                'avgRR': 0,
                'totalPnl': 0,
                'bestTrade': 0,
                'worstTrade': 0
            }
        
        wins = len([t for t in trades if t['pnl'] > 0])
        win_rate = round((wins / len(trades)) * 100)
        total_pnl = sum(t['pnl'] for t in trades)
        best_trade = max(t['pnl'] for t in trades)
        worst_trade = min(t['pnl'] for t in trades)
        
        return {
            'totalSignals': len(trades),
            'winRate': win_rate,
            'avgRR': 2.0,  # Approximation
            'totalPnl': total_pnl,
            'bestTrade': best_trade,
            'worstTrade': worst_trade
        }
    
    def _empty_stats(self):
        """Stats vides par défaut."""
        return {
            'global': {'winRate': 0, 'avgRR': 0, 'totalSignals': 0},
            'channels': {
                'channel1': {'totalSignals': 0, 'winRate': 0, 'avgRR': 0, 'totalPnl': 0, 'bestTrade': 0, 'worstTrade': 0},
                'channel2': {'totalSignals': 0, 'winRate': 0, 'avgRR': 0, 'totalPnl': 0, 'bestTrade': 0, 'worstTrade': 0}
            },
            'symbols': [],
            'accountType': self.account_type
        }
    
    def _extract_channel_from_comment(self, comment):
        """Extrait le numéro de canal du commentaire."""
        if not comment:
            return 1
        
        if 'Canal-2' in comment or 'Channel-2' in comment:
            return 2
        return 1
    
    def close_order(self, order_id):
        """Ferme un ordre."""
        try:
            # Convertir l'ID en entier
            ticket = int(order_id)
            
            # Vérifier si c'est une position ouverte
            position = mt5.positions_get(ticket=ticket)
            if position:
                pos = position[0]
                
                # Préparer la requête de fermeture
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                    "position": ticket,
                    "deviation": 20,
                    "magic": 234000,
                    "comment": f"Fermeture manuelle-{self.account_type}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    return {'success': True, 'message': f'Position fermée sur {self.account_type}'}
                else:
                    return {'success': False, 'message': f'Erreur: {result.comment if result else "Inconnue"}'}
            
            # Vérifier si c'est un ordre en attente
            order = mt5.orders_get(ticket=ticket)
            if order:
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": ticket,
                }
                
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    return {'success': True, 'message': f'Ordre annulé sur {self.account_type}'}
                else:
                    return {'success': False, 'message': f'Erreur: {result.comment if result else "Inconnue"}'}
            
            return {'success': False, 'message': 'Ordre non trouvé'}
            
        except Exception as e:
            return {'success': False, 'message': f'Erreur: {str(e)}'}

def get_account_selection():
    """Demande le choix du compte pour l'API."""
    print("\n📊 SÉLECTION DU COMPTE MT5 POUR L'API")
    print("=" * 40)
    print("1. MAT   - Compte MAT")
    print("2. DID   - Compte DID") 
    print("3. DEMO  - Compte Démo")
    print("=" * 40)
    
    while True:
        try:
            choice = input("Choisir le compte pour l'API (1/2/3): ").strip()
            
            if choice == '1':
                return 'MAT'
            elif choice == '2':
                return 'DID'
            elif choice == '3':
                return 'DEMO'
            else:
                print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3")
                
        except KeyboardInterrupt:
            print("\n❌ Annulé")
            exit()

# Sélection du compte au démarrage
if __name__ == '__main__':
    account_type = get_account_selection()
    print(f"✅ API configurée pour le compte {account_type}")
    
    # Instance globale de l'API
    trading_api = TradingAPI(account_type)

    # Routes API
    @app.route('/api/account', methods=['GET'])
    def get_account():
        account_info = trading_api.get_account_info()
        if account_info:
            return jsonify(account_info)
        return jsonify({'error': 'Impossible de récupérer les infos du compte'}), 500

    @app.route('/api/orders', methods=['GET'])
    def get_orders():
        orders = trading_api.get_open_orders()
        return jsonify(orders)

    @app.route('/api/history', methods=['GET'])
    def get_history():
        days = request.args.get('days', 7, type=int)
        history = trading_api.get_history(days)
        return jsonify(history)

    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        stats = trading_api.get_statistics()
        return jsonify(stats)

    @app.route('/api/orders/<order_id>/close', methods=['POST'])
    def close_order(order_id):
        result = trading_api.close_order(order_id)
        if result['success']:
            return jsonify(result)
        return jsonify(result), 400

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'mt5_connected': trading_api.is_connected,
            'account_type': trading_api.account_type,
            'timestamp': datetime.now().isoformat()
        })

    print("🚀 Démarrage du serveur API...")
    print(f"📊 Compte connecté: {account_type}")
    print("📊 Interface web: http://localhost:3000")
    print("🔌 API: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)