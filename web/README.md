# 🌐 Interface Web Trading Bot

Interface web Vue 3 pour le système de trading automatisé.

## 🚀 Installation

```bash
cd web
npm install
```

## 🔧 Développement

```bash
# Démarrer l'interface web
npm run dev

# Démarrer le serveur API (dans un autre terminal)
cd ..
python api_server.py
```

## 📊 Fonctionnalités

### 🏠 Dashboard
- Vue d'ensemble du compte (balance, équité, marge libre)
- Nombre de positions ouvertes
- Ordres récents avec P&L

### 📈 Ordres
- Liste complète des ordres ouverts et en attente
- Détails des signaux (canal d'origine)
- Filtrage par statut
- Fermeture manuelle des ordres

### 📚 Historique
- Historique des trades de la semaine
- Statistiques de performance
- Filtrage par période (semaine/mois/tout)
- Calcul automatique des durées

### 📊 Statistiques
- Win rate global et par canal
- Risk/Reward moyen
- Comparaison des performances entre canaux
- Statistiques par symbole
- Meilleurs/pires trades

## 🔌 API

L'interface communique avec le serveur Python via l'API REST:

- `GET /api/account` - Informations du compte
- `GET /api/orders` - Ordres ouverts/en attente
- `GET /api/history` - Historique des trades
- `GET /api/statistics` - Statistiques de performance
- `POST /api/orders/:id/close` - Fermer un ordre

## 🎨 Design

- **Framework**: Vue 3 + Vite
- **Styling**: Tailwind CSS
- **Icons**: Heroicons
- **Responsive**: Mobile-first design
- **Theme**: Interface moderne et professionnelle

## 📱 Responsive

L'interface s'adapte automatiquement:
- 📱 Mobile (320px+)
- 📱 Tablet (768px+)
- 💻 Desktop (1024px+)

## 🔄 Actualisation

- **Automatique**: Dashboard se met à jour toutes les 30s
- **Manuelle**: Boutons "Actualiser" sur chaque page
- **Temps réel**: Données synchronisées avec MT5

## 🛠️ Production

```bash
# Build pour production
npm run build

# Servir les fichiers statiques
npm run preview
```

L'interface est prête pour la production avec des données réelles via l'API MT5.