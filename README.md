# 🤖 Système de Trading Automatisé MT5

## 📋 Description

Système de trading automatisé qui surveille des canaux de signaux Telegram et exécute automatiquement des ordres sur MetaTrader 5. Le système supporte deux types de canaux avec des formats de signaux différents et inclut une gestion avancée des risques.

## 🏗️ Architecture du Système

```
📁 Système de Trading
├── 🎧 telegramListener.py    # Écouteur Telegram temps réel (PRODUCTION)
├── 🎧 messageListener.py     # Écouteur simulation (TESTS)
├── 🚀 launch_telegram_bot.py # Script de lancement production
├── 🤖 main.py               # Bot principal et orchestrateur
├── 📊 signalPaser.py        # Analyseur et validateur de signaux
├── 🧠 chatGpt.py            # Interface ChatGPT pour extraction
├── 💰 riskManager.py        # Gestionnaire de risques
├── 📈 order.py              # Gestionnaire d'ordres MT5
├── ℹ️  info.py              # Informations des instruments MT5
├── ⚙️  config.py            # Configuration système
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

## ⚙️ Configuration

### 📋 Prérequis
```bash
pip install -r requirements.txt
```

### 🔑 Variables d'Environnement
Créer un fichier `.env`:
```env
# Configuration Telegram
TELEGRAM_MAT_API_ID=YOUR_API_ID
TELEGRAM_MAT_API_HASH=YOUR_API_HASH
TELEGRAM_MAT_SESSION=MAT.session
TELEGRAM_CHANNEL_1_ID=-2125503665
TELEGRAM_CHANNEL_2_ID=-2259371711

# Configuration Trading
TOTAL_RISK_EUR=300.0
MAX_RISK_PERCENTAGE=7.0
GPT_KEY=YOUR_OPENAI_API_KEY

# Configuration MT5 (COMPTE DÉMO OBLIGATOIRE)
MT5_DEMO_LOGIN=YOUR_DEMO_LOGIN
MT5_DEMO_MDP=YOUR_DEMO_PASSWORD
MT5_DEMO_SERVEUR=YOUR_DEMO_SERVER
```

## 🚀 Utilisation

### 🎯 Mode Production (Telegram Réel)
```bash
python launch_telegram_bot.py
```
- ✅ Connexion Telegram temps réel
- ✅ Surveillance automatique des canaux
- ✅ Placement d'ordres automatique
- ✅ Connexion forcée au compte démo

### 🧪 Mode Test (Simulation)
```bash
python main.py
```
- ✅ Tests sans connexion Telegram
- ✅ Simulation de signaux
- ✅ Validation du système

## 📚 Guide des Fonctions Principales

### 🤖 TradingBot

#### `process_signal(signal_text, channel_id)`
Traite un signal pour un canal spécifique.
```python
bot = TradingBot()
result = bot.process_signal(signal_text, channel_id=1)
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

### 📈 SendOrder

#### `place_signal_orders(signals, lot_sizes, channel_id)`
Place tous les ordres d'un signal sur MT5.

## 🔒 Sécurité

- ✅ **Compte démo obligatoire** - Connexion forcée au compte démo
- ✅ **Validation stricte** des signaux
- ✅ **Limites de risque** configurables
- ✅ **Vérifications** avant chaque ordre
- ✅ **Historique complet** des actions
- ✅ **Gestion d'erreurs** robuste

## 🎯 Exemple de Déroulement Complet

### 1. 🎬 Initialisation
```python
# Le système se lance automatiquement
python launch_telegram_bot.py
```

### 2. 📡 Réception d'un Message
```
🆕 Nouveau message détecté dans le Canal 1
💬 Contenu: XAUUSD BUY NOW @ 2329.79...
```

### 3. 🔍 Validation du Signal
- Vérification format signal
- Extraction via ChatGPT
- Validation des prix

### 4. 🛡️ Vérification des Risques
- Vérification limite compte (7%)
- Calcul tailles de lot optimales
- Validation avant placement

### 5. 📈 Placement des Ordres
```
✅ 3 ordres placés sur MT5:
- Ordre 1: 0.05 lots → TP1 @ 2350.00
- Ordre 2: 0.05 lots → TP2 @ 2375.00  
- Ordre 3: 0.05 lots → TP3 @ 2403.50
```

## 🐛 Dépannage

### ❌ Erreurs Communes

#### "MT5 n'est pas connecté"
- Vérifier que MetaTrader 5 est ouvert
- Vérifier les identifiants démo dans .env
- Le système se connecte automatiquement au compte démo

#### "Impossible d'extraire le signal"
- Vérifier la clé API OpenAI
- Vérifier le format du signal
- Consulter les logs ChatGPT

#### "Risque trop élevé"
- Vérifier les positions ouvertes
- Ajuster le paramètre `MAX_RISK_PERCENTAGE`
- Fermer des positions si nécessaire

## 📈 Performance

- ⚡ **Traitement temps réel** des signaux
- 🔄 **Surveillance continue** des canaux
- 📊 **Calculs optimisés** des lots
- 💾 **Historique persistant**
- 🎯 **Exécution précise** des ordres
- 🛡️ **Sécurité maximale** (compte démo)

---

*Système prêt pour la production avec sécurité maximale (compte démo obligatoire).*