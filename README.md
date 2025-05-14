# RouleMaPoulette - Système de Réservation de Véhicules

## Description du projet
RouleMaPoulette est un système de gestion de location de véhicules développé dans le cadre du cours UE 2.1 - Modélisation des systèmes à l'ENSTA Bretagne. Ce projet propose une interface complète pour la gestion d'un parc automobile de location, intégrant la réservation de véhicules, la gestion du parc, l'émission de factures et l'optimisation des ressources.

## Fonctionnalités principales
- Gestion des réservations de véhicules
- Gestion du parc automobile (disponibilité, coûts, entretien)
- Attribution intelligente de véhicules selon les critères clients
- Génération de factures au format PDF
- Analyse et optimisation du parc basée sur l'historique d'utilisation
- Interface utilisateur console (avec évolution future vers GUI)

## Architecture du projet
Le projet adopte une architecture MVC (Modèle-Vue-Contrôleur) pour une séparation claire des responsabilités:

```
projet_location/
│
├── model/                     # Modèles de données et logique métier
│   ├── __init__.py
│   ├── vehicule.py            # Classes de véhicules (base + spécialisées)
│   ├── client.py              # Gestion des clients
│   ├── reservation.py         # Gestion des réservations
│   ├── parc.py                # Gestion du parc automobile
│   └── facture.py             # Génération de factures
│
├── view/                      # Interfaces utilisateur
│   ├── __init__.py
│   └── console_view.py        # Interface console
│
├── controller/                # Coordination entre modèles et vues
│   ├── __init__.py
│   ├── client_controller.py
│   ├── reservation_controller.py
│   └── parc_controller.py
│
├── utils/                     # Fonctions utilitaires
│   ├── __init__.py
│   ├── database.py            # Gestion de la base de données SQLite
│   ├── pdf_generator.py       # Génération de documents PDF
│   └── optimisation.py        # Algorithmes d'optimisation du parc
│
├── tests/                     # Tests unitaires
│   ├── __init__.py
│   ├── test_vehicule.py
│   ├── test_client.py
│   ├── test_reservation.py
│   ├── test_parc.py
│   └── test_facture.py
│
└── main.py                    # Point d'entrée de l'application
```

## Modèles principaux

### Classe Vehicule (abstraite)
- Base pour tous les types de véhicules
- Attributs communs: id, marque, modèle, année, kilométrage, etc.
- Méthodes: calculer_cout_possession(), calculer_tarif_journalier() (abstraite)

#### Classes dérivées
- **Voiture**: Attributs spécifiques (places, puissance, carburant, options)
- **Utilitaire**: Attributs spécifiques (volume, charge utile, hayon)
- **Moto**: Attributs spécifiques (cylindrée, type)

### Classe Parc
- Gestion centralisée des véhicules et réservations
- Méthodes pour vérifier la disponibilité, ajouter/retirer des véhicules
- Fonction récursive pour vérifier les périodes de disponibilité
- Algorithme d'optimisation du parc basé sur l'historique d'utilisation

### Classe Reservation
- Gestion du cycle de vie des réservations
- Calcul du prix total avec application de remises pour longue durée
- Gestion des statuts (confirmée, annulée, terminée)

### Classe Facture
- Génération de documents au format PDF
- Utilisation du pattern Strategy pour différents formats de documents

## Patterns de conception implémentés
1. **MVC** (Modèle-Vue-Contrôleur): Architecture globale du projet
2. **Strategy**: Pour la génération flexible de documents (Facture)
3. **Observer**: Pour notifier les clients des changements dans leurs réservations
4. **Héritage/Polymorphisme**: Pour la hiérarchie des véhicules
5. **Composite**: Pour la gestion du parc de véhicules

## Base de données
Le projet utilise SQLite pour la persistance des données, avec une classe Database qui implémente les opérations CRUD pour toutes les entités du système.

## Prérequis
- Python 3.8 ou supérieur
- Bibliothèques requises:
  - sqlite3
  - datetime
  - fpdf (pour la génération de PDF)
  - matplotlib (pour les visualisations statistiques)

## Installation des dépendances
```bash
pip install fpdf matplotlib
```

## Comment lancer le programme
```bash
python main.py
```

## Tests
Pour exécuter les tests unitaires:
```bash
python -m unittest discover tests
```

Pour tester un module spécifique:
```bash
python -m unittest tests.test_vehicule
```

## Limitations actuelles
- Tarification simplifiée (pas de gestion dynamique des prix)
- Interface console uniquement (GUI prévue en phase 2)
- Gestion limitée des cas complexes d'annulation
- Pas de gestion des dommages et pénalités

## Perspectives d'évolution
- Tarification dynamique selon la saison et la demande
- Application mobile pour les clients
- Intégration de services tiers (assurances, assistance)
- Système de fidélité pour les clients réguliers
- Paiements en ligne sécurisés
- Utilisation de l'IA pour optimiser la gestion du parc

## Auteurs
- Marina TAVERNIER (marina.tavernier@entsa.fr)
- Pierre CHALOPIN (pierre.chalopin@ensta.fr)

## Licence
Ce projet est développé dans le cadre académique de l'ENSTA Bretagne.
