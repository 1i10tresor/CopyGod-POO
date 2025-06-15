# 🤖 Système de Trading Automatisé MT5

## 📋 Description

Système de trading automatisé qui surveille des canaux de signaux et exécute automatiquement des ordres sur MetaTrader 5. Le système supporte deux types de canaux avec des formats de signaux différents et inclut une gestion avancée des risques.

## 🏗️ Architecture du Système

```
📁 Système de Trading
├── 🎧 messageListener.py     # Écouteur de messages des canaux
├── 🤖 main.py               # Bot principal et orchestrateur
├── 📊 signalPaser.py        # Analyseur et validateur de signaux
├── 🧠 chatGpt.py            # Interface ChatGPT pour extraction
├── 💰 riskManager.py        # Gestionnaire de risques
├── 📈 order.py              # Gestionnaire d'ordres MT5
├── ℹ️  info.py              # Informations des instruments MT5
└── 📖 README.md             # Documentation
```

## 🔧 Fonctionnalités Principales

### 🎯 Canaux Supportés

#### 📡 Canal 1 - Format Standard
- **Format**: `SYMBOL DIRECTION @ ENTRY, SL @ XX, TP1 @ XX, TP2 @ XX, TP3 @ XX`
- **Exemple**: 
  ```
  XAUUSD BUY NOW @ 2329.79
  SL @ 2314.90
  TP1 @ 2350.00
  TP2 @ 2375.00
  TP3 @ 2403.50
  ```
- **Comportement**: 3 ordres avec même entrée, 3 TPs différents
- **TP3 "open"**: Si TP3 = "open", calcul automatique (2x distance TP2)

#### 📡 Canal 2 - Format Fourchette
- **Format**: `DIRECTION XXXX-XX, TP XXXX, SL XX`
- **Exemple**: 
  ```
  go sell 3349-52
  tp 3330
  sl 54.5
  ```
- **Comportement**: 3 ordres avec entrées différentes, RR fixes (2.5, 4, 6)
- **Fourchettes**: `3349-52` → entrées [3349, 3350.5, 3352]
- **SL abrégé**: `sl 54.5` → `3354.5` (base + SL)

### 🛡️ Gestion des Risques
- **Risque total**: 300€ par signal (configurable)
- **Limite compte**: 7% maximum du capital en risque
- **Calcul automatique**: Tailles de lot basées sur distance SL
- **Blocage**: Aucun nouvel ordre si limite dépassée

### 🎧 Écouteur de Messages
- **Surveillance**: Canaux 1 et 2 en temps réel
- **Détection**: Signaux valides automatiquement
- **Traitement**: Exécution immédiate des ordres
- **Historique**: Suivi de tous les messages traités

## 📚 Guide des Fonctions

### 🎧 MessageListener

#### `start_listening()`
Démarre l'écoute des canaux en arrière-plan.
```python
listener.start_listening()
```

#### `simulate_message(channel_id, content, author)`
Simule un message pour les tests.
```python
listener.simulate_message(1, "EURUSD BUY @ 1.0850...", "TestUser")
```

#### `display_listener_summary()`
Affiche les statistiques de l'écouteur.

### 🤖 TradingBot

#### `process_signal(signal_text, channel_id)`
Traite un signal pour un canal spécifique.
```python
bot.process_signal(signal_text, channel_id=1)
```

#### `process_signal_auto(signal_text)`
Détection automatique du canal et traitement.
```python
bot.process_signal_auto(signal_text)
```

#### `get_account_summary()`
Affiche le résumé complet du compte.

### 📊 SignalProcessor

#### `is_signal()`
Vérifie si le texte contient un signal valide.

#### `get_signal()`
Extrait et valide le signal selon le canal.

### 💰 RiskManager

#### `can_open_position(order_sender)`
Vérifie si de nouvelles positions peuvent être ouvertes.

#### `calculate_lot_size_for_signal(signals, channel_id)`
Calcule les tailles de lot optimales.

#### `display_risk_status(order_sender)`
Affiche le statut détaillé des risques.

### 📈 SendOrder

#### `place_signal_orders(signals, lot_sizes, channel_id)`
Place tous les ordres d'un signal sur MT5.

#### `get_account_info()`
Récupère les informations du compte MT5.

#### `get_open_positions()`
Retourne les positions ouvertes.

### ℹ️ Infos

#### `get_symbol_info(symbol)`
Récupère les informations d'un instrument via MT5.

#### `get_pip_value_eur(symbol, lot_size)`
Calcule la valeur d'un pip en EUR.

## 🚀 Exemple de Déroulement Complet

### 1. 🎬 Initialisation
```python
# Création du système
system = TradingSystem(total_risk_eur=300.0, max_risk_percentage=7.0)

# Démarrage
system.start_system()
```

### 2. 📡 Réception d'un Message
```
🆕 Nouveau message détecté dans le Canal 1
📝 ID: msg_001
👤 Auteur: TradingSignals
💬 Contenu:
XAUUSD BUY NOW @ 2329.79
SL @ 2314.90
TP1 @ 2350.00
TP2 @ 2375.00
TP3 @ 2403.50
```

### 3. 🔍 Validation du Signal
```python
# Vérification que c'est un signal valide
processor = SignalProcessor(signal, channel_id=1)
if processor.is_signal():
    # Extraction via ChatGPT
    signal_data = processor.get_signal()
```

### 4. 🛡️ Vérification des Risques
```python
# Vérification du risque du compte
if risk_manager.can_open_position(order_sender):
    # Calcul des tailles de lot
    lot_sizes = risk_manager.calculate_lot_size_for_signal(signal_data, 1)
```

### 5. 📈 Placement des Ordres
```python
# Placement sur MT5
orders = order_sender.place_signal_orders(signal_data, lot_sizes, 1)

# Résultat : 3 ordres placés
# - Ordre 1: 0.05 lots → TP1 @ 2350.00
# - Ordre 2: 0.05 lots → TP2 @ 2375.00  
# - Ordre 3: 0.05 lots → TP3 @ 2403.50
```

### 6. 📊 Suivi et Historique
```python
# Enregistrement dans l'historique
processed_record = {
    'channel_id': 1,
    'orders_placed': 3,
    'processing_result': True,
    'timestamp': datetime.now()
}
```

## ⚙️ Configuration

### 📋 Prérequis
```bash
pip install -r requirements.txt
```

### 🔑 Variables d'Environnement
Créer un fichier `.env`:
```
GPT_KEY=your_openai_api_key_here
```

### 🎛️ Paramètres Configurables
```python
# Dans main.py
bot = TradingBot(
    total_risk_eur=300.0,      # Risque total par signal
    max_risk_percentage=7.0     # Limite de risque du compte
)
```

## 🚀 Utilisation

### 🎯 Utilisation Basique
```python
from main import TradingBot

# Créer le bot
bot = TradingBot(total_risk_eur=300.0)

# Traiter un signal manuellement
signal_text = "EURUSD BUY @ 1.0850, SL @ 1.0800, TP1 @ 1.0900..."
result = bot.process_signal(signal_text, channel_id=1)
```

### 🤖 Système Automatique Complet
```python
from messageListener import TradingSystem

# Créer et démarrer le système complet
system = TradingSystem()
system.start_system()

# Le système surveille automatiquement les canaux
# et traite les signaux en temps réel
```

### 🧪 Tests et Simulation
```python
# Simuler des messages pour tester
system.listener.simulate_message(1, signal_canal_1, "TestUser")
system.listener.simulate_message(2, signal_canal_2, "TestUser")

# Afficher les résultats
system.display_full_summary()
```

## 🔧 Personnalisation

### 📡 Ajouter un Nouveau Canal
1. Modifier `supported_channels` dans `main.py`
2. Ajouter la logique dans `SignalProcessor`
3. Mettre à jour le prompt ChatGPT
4. Implémenter la logique de placement d'ordres

### 🛡️ Modifier la Gestion des Risques
```python
# Dans riskManager.py
def __init__(self, total_risk_eur, max_risk_percentage=7.0):
    self.total_risk_eur = total_risk_eur
    self.max_risk_percentage = max_risk_percentage  # Modifier ici
```

### 🎯 Personnaliser les RR du Canal 2
```python
# Dans signalPaser.py
rr_ratios = [2.5, 4, 6]  # Modifier les ratios Risk/Reward
```

## 🐛 Dépannage

### ❌ Erreurs Communes

#### "MT5 n'est pas connecté"
- Vérifier que MetaTrader 5 est ouvert
- Vérifier les paramètres de connexion
- Redémarrer MT5 si nécessaire

#### "Impossible d'extraire le signal"
- Vérifier la clé API OpenAI
- Vérifier le format du signal
- Consulter les logs ChatGPT

#### "Risque trop élevé"
- Vérifier les positions ouvertes
- Ajuster le paramètre `max_risk_percentage`
- Fermer des positions si nécessaire

### 📊 Logs et Monitoring
Le système affiche des logs détaillés pour chaque étape :
- 🆕 Nouveaux messages détectés
- ✅ Signaux validés
- 💰 Calculs de risque
- 📈 Ordres placés
- ❌ Erreurs rencontrées

## 🔒 Sécurité

- ✅ Validation stricte des signaux
- ✅ Limites de risque configurables
- ✅ Vérifications avant chaque ordre
- ✅ Historique complet des actions
- ✅ Gestion d'erreurs robuste

## 📈 Performance

- ⚡ Traitement en temps réel
- 🔄 Surveillance continue des canaux
- 📊 Calculs optimisés des lots
- 💾 Historique persistant
- 🎯 Exécution précise des ordres

---

*Système développé pour un trading automatisé sécurisé et efficace sur MetaTrader 5.*