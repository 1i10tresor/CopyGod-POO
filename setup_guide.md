# 🔧 Guide de Configuration

## 📋 Étapes de Configuration

### 1. 🔑 Créer le fichier .env
```bash
cp .env.example .env
```

### 2. 📱 Configuration Telegram
1. Aller sur https://my.telegram.org/apps
2. Créer une nouvelle application
3. Récupérer `API_ID` et `API_HASH`
4. Remplir dans le `.env`:
```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

### 3. 🤖 Configuration OpenAI
1. Aller sur https://platform.openai.com/api-keys
2. Créer une nouvelle clé API
3. Remplir dans le `.env`:
```env
GPT_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. 📈 Configuration MT5
Pour chaque compte (MAT, DID, DEMO), remplir:
```env
# Exemple pour le compte MAT
MT5_MAT_LOGIN=12345678
MT5_MAT_PASSWORD=VotreMotDePasse
MT5_MAT_SERVER=VotreServeur-Demo
```

### 5. ✅ Vérification
Lancer le test de configuration:
```bash
python test_config.py
```

## 🚨 Erreurs Communes

### "API ID or Hash cannot be empty"
- Vérifier que `TELEGRAM_API_ID` et `TELEGRAM_API_HASH` sont remplis
- Vérifier qu'il n'y a pas d'espaces avant/après les valeurs

### "Identifiants MT5 manquants"
- Vérifier que les 3 champs sont remplis pour le compte choisi
- Vérifier que le login est un nombre (sans guillemets)

### "Connexion MT5 échouée"
- Vérifier que MetaTrader 5 est installé et ouvert
- Vérifier les identifiants de connexion
- Tester la connexion manuelle dans MT5