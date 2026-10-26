# Güdlft - Plateforme de réservation de compétitions

Bienvenue sur le dépôt du projet **Güdlft**. Il s'agit d'une version allégée (POC) de notre système de réservation pour les organisateurs de compétitions locales et régionales.

L'application permet aux secrétaires de clubs de se connecter, de consulter les compétitions à venir, et d'utiliser les points accumulés par leur club pour réserver des places pour leurs athlètes.

## 🚀 Fonctionnalités principales
- **Authentification** : Connexion sécurisée pour les secrétaires de clubs via leur adresse e-mail.
- **Réservation de places** : Achat de places pour les compétitions en utilisant les points du club (1 point = 1 place).
- **Tableau des points** : Consultation publique (lecture seule) des points de tous les clubs pour garantir la transparence.
- **Règles métier strictes** : 
  - Maximum de 12 places par club et par compétition.
  - Interdiction de réserver plus de places que le stock disponible.
  - Interdiction de réserver pour une compétition passée.

## 🛠️ Technologies utilisées
- **Python 3.6+**
- **Flask** (Micro-framework web)
- **JSON** (Stockage des données : `clubs.json` et `competitions.json`)
- **Pytest** (Tests unitaires, d'intégration et fonctionnels)
- **Locust** (Tests de performance)
- **Flake8** (Qualité et style du code)

## 📦 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/micheloulai93-creator/Python_Testing_2627.git
   cd Python_Testing_2627-main