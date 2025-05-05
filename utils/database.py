# utils/database.py
# ici on introduit les classes pour gérer la BDD SQLite

import sqlite3
from datetime import datetime


class Database:
    """
    gère la connexion et opération sur notre BDD
    """

    def __init__(self, db_path="location.db"):
        """
        initialisation de la BDD
        création si la table n'éxiste pas

        Args:
            db_path (str): Chemin vers le fichier de base de données
        """
        # connexion à la BDD
        self.conn = sqlite3.connect(db_path)

        # config pour récupérer des résultats comme des dictionnaires
        self.conn.row_factory = sqlite3.Row

        # création de cusreur pour faire des requêtes, méthode classique avec sqlite3
        self.cursor = self.conn.cursor()

        # crée la table si elle n'éxiste pas
        self._creer_tables()

    def _creer_tables(self):
        """
        crée les tables si non éxistant
        """
        # table des véhicules avec les attributs qui correspondent au clé dans implementation des classes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicules (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            marque TEXT NOT NULL,
            modele TEXT NOT NULL,
            annee INTEGER NOT NULL,
            kilometrage INTEGER NOT NULL,
            prix_achat REAL NOT NULL,
            cout_entretien_annuel REAL NOT NULL,
            categorie TEXT NOT NULL,
            attributs_specifiques TEXT NOT NULL
        )
        ''')

        # table des clients idem
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            adresse TEXT NOT NULL,
            telephone TEXT NOT NULL,
            email TEXT NOT NULL
        )
        ''')

        # table des réservations idem
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL,
            vehicule_id INTEGER NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            prix_total REAL,
            statut TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (vehicule_id) REFERENCES vehicules (id)
        )
        ''')

        # table des factures idem
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY,
            reservation_id INTEGER NOT NULL,
            date_emission TEXT NOT NULL,
            montant_ht REAL NOT NULL,
            taux_tva REAL NOT NULL,
            montant_ttc REAL NOT NULL,
            FOREIGN KEY (reservation_id) REFERENCES reservations (id)
        )
        ''')

        # validation des changement, propre à sqlite3 et sa synthaxe
        self.conn.commit()

    def fermer(self):
        """
        ferme la connection à la BDD
        """
        if self.conn:
            self.conn.close()

    # -------------------------------------------------
    # Méthodes CRUD pour les véhicules - implémentation
    # -------------------------------------------------

    def sauvegarder_vehicule(self, vehicule):
        """
        sauvegarde un véhicule dans la BDD

        Args:
            vehicule: Objet de type Vehicule

        Returns:
            int: ID du véhicule sauvegardé
        """
        # TODO: Implémenter la sauvegarde complète des véhicules
        # Cette méthode devra:
        # 1. Sérialiser les attributs spécifiques selon le type de véhicule
        # 2. Insérer ou mettre à jour les données en base
        # 3. Assigner l'ID généré au véhicule si c'est une nouvelle insertion

        # Version minimale pour le moment:
        print(f"Sauvegarde du véhicule {vehicule.marque} {vehicule.modele}")
        return 1  # ID factice

    def charger_vehicule(self, vehicule_id):
        """
        charge un véhicule depuis la BDD.

        Args:
            vehicule_id (int): ID du véhicule à charger

        Returns:
            Vehicule: Objet véhicule correspondant, ou None si non trouvé
        """
        # TODO: Implémenter le chargement complet des véhicules
        # Cette méthode devra:
        # 1. Charger les données depuis la base
        # 2. Désérialiser les attributs spécifiques
        # 3. Créer l'objet du bon type (Voiture, Utilitaire, Moto)

        # Version minimale qui retourne None
        return None

    # --------------------------------
    # Méthodes CRUD pour les clients - à implémenter
    # --------------------------------

    def sauvegarder_client(self, client):
        """
        Sauvegarde un client dans la base de données.

        Args:
            client: Objet de type Client

        Returns:
            int: ID du client sauvegardé
        """
        # TODO: Implémenter cette méthode
        print(f"Sauvegarde du client {client.prenom} {client.nom}")
        return 1  # ID factice

    def charger_client(self, client_id):
        """
        Charge un client depuis la base de données.

        Args:
            client_id (int): ID du client à charger

        Returns:
            Client: Objet client correspondant, ou None si non trouvé
        """
        # TODO: Implémenter cette méthode
        return None

    # --------------------------------
    # Méthodes CRUD pour les réservations - à implémenter
    # --------------------------------

    def sauvegarder_reservation(self, reservation):
        """
        Sauvegarde une réservation dans la base de données.

        Args:
            reservation: Objet de type Reservation

        Returns:
            int: ID de la réservation sauvegardée
        """
        # TODO: Implémenter cette méthode
        print(f"Sauvegarde d'une réservation pour le véhicule {reservation.vehicule_id}")
        return 1  # ID factice

    def charger_reservation(self, reservation_id):
        """
        Charge une réservation depuis la base de données.

        Args:
            reservation_id (int): ID de la réservation à charger

        Returns:
            Reservation: Objet réservation correspondant, ou None si non trouvé
        """
        # TODO: Implémenter cette méthode
        return None

    # --------------------------------
    # Méthodes CRUD pour les factures - à implémenter
    # --------------------------------

    # TODO: Ajouter les méthodes pour les factures

    # --------------------------------
    # Méthodes de recherche avancée - à implémenter plus tard
    # --------------------------------

    # TODO: Ajouter des méthodes de recherche avancée pour chaque entité


# Exemple d'utilisation minimale pour l'instant
if __name__ == "__main__":
    # Création d'une instance de la base de données
    db = Database("test.db")
    print("Base de données initialisée")

    # TODO: Ajouter des exemples de création et manipulation de données

    # fermeture de la connexion
    db.fermer()