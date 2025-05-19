# utils/database.py
# ce fichier contient la classe database pour gérer la base de données sqlite
# 1. Imports
# 2. Classe Database
#    ├── Initialisation (__init__)
#    ├── Création des tables (_creer_tables)
#    ├── Méthodes pour Véhicules
#    │   ├── sauvegarder_vehicule
#    │   ├── charger_vehicule
#    │   ├── charger_tous_vehicules
#    │   ├── supprimer_vehicule
#    │   └── rechercher_vehicules
#    ├── Méthodes pour Clients (même structure)
#    ├── Méthodes pour Réservations (même structure)
#    ├── Méthodes pour Factures (même structure)
#    └── Génération de données test
#
# Demande utilisateur → Vue
# Vue → Contrôleur
# Contrôleur → Database (pour lire/écrire)
# Database ↔ SQLite (fichier .db)
# Database → Contrôleur (retourne des objets métier)
# Contrôleur → Vue (avec objets métier)
# Vue → Réponse utilisateur
#
# utils/database.py
# ce fichier implémente la couche d'accès aux données (DAL) pour l'ensemble du système
# il fait partie des composants fondamentaux de l'architecture MVC, assurant la persistance
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                       STRUCTURE DU MODULE DATABASE                        │
# ├───────────────────────────────────────────────────────────────────────────┤
# │ ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐        │
# │ │    Véhicules    │    │     Clients     │    │   Réservations   │        │
# │ ├─────────────────┤    ├─────────────────┤    ├──────────────────┤        │
# │ │ Sauvegarder     │    │ Sauvegarder     │    │ Sauvegarder      │        │
# │ │ Charger         │    │ Charger         │    │ Charger          │        │
# │ │ Supprimer       │    │ Supprimer       │    │ Supprimer        │        │
# │ │ Rechercher      │    │ Rechercher      │    │ Rechercher       │        │
# │ └─────────────────┘    └─────────────────┘    └──────────────────┘        │
# │ ┌─────────────────┐    ┌─────────────────────────────────────────┐        │
# │ │    Factures     │    │         Utilitaires & Tests             │        │
# │ ├─────────────────┤    ├─────────────────────────────────────────┤        │
# │ │ Sauvegarder     │    │ Création tables   │ Fermeture connexion │        │
# │ │ Charger         │    │ Génération test   │ Gestion erreurs     │        │
# │ │ Supprimer       │    └─────────────────────────────────────────┘        │
# │ └─────────────────┘                                                       │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                      SCHÉMA DE LA BASE DE DONNÉES                         │
# ├───────────────────────────────────────────────────────────────────────────┤
# │                                                                           │
# │  ┌───────────────┐        ┌────────────────┐        ┌───────────────┐    │
# │  │   vehicules   │        │  reservations  │        │    clients    │    │
# │  ├───────────────┤      ┌─┴────────────────┤        ├───────────────┤    │
# │  │ id (PK)       │      │ id (PK)          │        │ id (PK)       │    │
# │  │ type          │      │ client_id (FK) ──┼────────► nom           │    │
# │  │ marque        │◄─────┼─ vehicule_id (FK)│        │ prenom        │    │
# │  │ modele        │      │ date_debut       │        │ adresse       │    │
# │  │ annee         │      │ date_fin         │        │ telephone     │    │
# │  │ kilometrage   │      │ prix_total       │        │ email         │    │
# │  │ prix_achat    │      │ statut           │        └───────────────┘    │
# │  │ cout_entretien│      └───┬──────────────┘                             │
# │  │ categorie     │          │                       ┌───────────────┐    │
# │  │ attributs_json│          │                       │   factures    │    │
# │  └───────────────┘          │                       ├───────────────┤    │
# │                             │                       │ id (PK)       │    │
# │                             └───────────────────────► reservation_id│    │
# │                                                     │ date_emission │    │
# │                                                     │ montant_ht    │    │
# │                                                     │ taux_tva      │    │
# │                                                     │ montant_ttc   │    │
# │                                                     └───────────────┘    │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                    FLUX D'INTERACTIONS AVEC LES AUTRES MODULES            │
# ├───────────────────────────────────────────────────────────────────────────┤
# │                                                                           │
# │  ┌────────────────┐  ┌───────────────┐  ┌────────────────────┐            │
# │  │  Vue (PyQt5)   │  │  Contrôleurs  │  │ Modèles (Objets)   │            │
# │  └───────┬────────┘  └───────┬───────┘  └──────────┬─────────┘            │
# │          │    ▲               │    ▲               │    ▲                 │
# │   requête│    │ objet         │    │ objets        │    │ instances       │
# │      user│    │ métier        │    │ métier        │    │ chargées        │
# │          ▼    │               ▼    │               ▼    │                 │
# │  ┌───────────────────────────────────────────────────────────────┐        │
# │  │                          DATABASE                             │        │
# │  ├───────────────────────────────────────────────────────────────┤        │
# │  │                                                               │        │
# │  │ ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐   │        │
# │  │ │ Traduction    │  │ Conversion   │  │ Sérialisation des  │   │        │
# │  │ │ objet/SQL     │  │ des types    │  │ attributs en JSON  │   │        │
# │  │ └───────────────┘  └──────────────┘  └────────────────────┘   │        │
# │  │                                                               │        │
# │  │ ┌────────────────────────────────────────────────────────┐    │        │
# │  │ │              SQLite (Moteur de stockage)               │    │        │
# │  │ └────────────────────────────────────────────────────────┘    │        │
# │  └───────────────────────────────────────────────────────────────┘        │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │                  PRINCIPALES INTERACTIONS PAR CONTRÔLEUR                  │
# ├───────────────────────────────────────────────────────────────────────────┤
# │                                                                           │
# │  ┌──────────────────────┐      ┌──────────────────────────────────────┐   │
# │  │   ParcController     │      │ ► sauvegarder_vehicule()             │   │
# │  │                      │──────┤ ► charger_vehicule(id)               │   │
# │  │   (parc_controller)  │      │ ► supprimer_vehicule(id)             │   │
# │  └──────────────────────┘      │ ► rechercher_vehicules(criteres)     │   │
# │                                └──────────────────────────────────────┘   │
# │                                                                           │
# │  ┌──────────────────────┐      ┌──────────────────────────────────────┐   │
# │  │   ClientController   │      │ ► sauvegarder_client()               │   │
# │  │                      │──────┤ ► charger_client(id)                 │   │
# │  │ (client_controller)  │      │ ► supprimer_client(id)               │   │
# │  └──────────────────────┘      │ ► rechercher_clients(criteres)       │   │
# │                                └──────────────────────────────────────┘   │
# │                                                                           │
# │  ┌──────────────────────┐      ┌──────────────────────────────────────┐   │
# │  │ ReservationController│      │ ► sauvegarder_reservation()          │   │
# │  │                      │──────┤ ► charger_reservation(id)            │   │
# │  │   (reservation_ctrl) │      │ ► charger_reservations_client(id)    │   │
# │  └──────────────────────┘      │ ► charger_reservations_vehicule(id)  │   │
# │                                └──────────────────────────────────────┘   │
# └───────────────────────────────────────────────────────────────────────────┘
#
# particularités techniques:
# - utilise SQLite comme moteur de base de données embarqué
# - emploie le pattern Row Factory pour récupérer les résultats sous forme de dictionnaires
# - sérialise les attributs spécifiques en JSON pour gérer le polymorphisme
# - maintient les références d'intégrité via contraintes FOREIGN KEY
# - convertit automatiquement les dates entre formats Python et SQLite
# - implémente des vérifications de sécurité avant suppressions (dépendances)
# - fournit une méthode de génération de données de test pour le développement
# - centralise les transactions et gestion des erreurs SQLite

import sqlite3
import json
from datetime import datetime


class Database:
    """
    classe gérant la connexion et les opérations sur la base de données sqlite
    """

    def __init__(self, db_path):
        """
        initialise la connexion à la base de données

        args:
            db_path: chemin vers le fichier sqlite
        """
        # connexion à la base de données
        self.conn = sqlite3.connect(db_path)
        # configuration pour avoir les résultats sous forme de dictionnaire
        self.conn.row_factory = sqlite3.Row
        # création d'un curseur pour exécuter les requêtes
        self.cursor = self.conn.cursor()
        # création des tables si elles n'existent pas
        self._creer_tables()

    def _creer_tables(self):
        """
        crée les tables nécessaires si elles n'existent pas
        """
        # table des véhicules
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

        # table des clients
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

        # table des réservations
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL,
            vehicule_id INTEGER NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            prix_total REAL NOT NULL,
            statut TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (vehicule_id) REFERENCES vehicules (id)
        )
        ''')

        # table des factures
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

        # validation des changements
        self.conn.commit()

    def fermer(self):
        """
        ferme la connexion à la base de données
        """
        if self.conn:
            self.conn.close()

    # méthodes pour les véhicules

    def sauvegarder_vehicule(self, vehicule):
        """
        sauvegarde un véhicule dans la base de données

        args:
            vehicule: objet de type vehicule

        returns:
            int: id du véhicule sauvegardé
        """
        # extraction du type de véhicule
        type_vehicule = vehicule.__class__.__name__

        # préparation des attributs spécifiques selon le type
        attributs_specifiques = {}

        if type_vehicule == "Voiture":
            attributs_specifiques = {
                "nb_places": vehicule.nb_places,
                "puissance": vehicule.puissance,
                "carburant": vehicule.carburant,
                "options": vehicule.options
            }
        elif type_vehicule == "Utilitaire":
            attributs_specifiques = {
                "volume": vehicule.volume,
                "charge_utile": vehicule.charge_utile,
                "hayon": vehicule.hayon
            }
        elif type_vehicule == "Moto":
            attributs_specifiques = {
                "cylindree": vehicule.cylindree,
                "type": vehicule.type
            }

        # conversion en json pour stockage
        attributs_json = json.dumps(attributs_specifiques)

        # vérification si le véhicule existe déjà
        if vehicule.id is None:
            # création d'un nouveau véhicule
            self.cursor.execute("""
            INSERT INTO vehicules
            (type, marque, modele, annee, kilometrage, prix_achat, 
            cout_entretien_annuel, categorie, attributs_specifiques)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                type_vehicule,
                vehicule.marque,
                vehicule.modele,
                vehicule.annee,
                vehicule.kilometrage,
                vehicule.prix_achat,
                vehicule.cout_entretien_annuel,
                vehicule.categorie,
                attributs_json
            ))

            # récupération de l'id généré
            vehicule.id = self.cursor.lastrowid
        else:
            # mise à jour d'un véhicule existant
            self.cursor.execute("""
            UPDATE vehicules
            SET type = ?, marque = ?, modele = ?, annee = ?, kilometrage = ?, 
                prix_achat = ?, cout_entretien_annuel = ?, categorie = ?, 
                attributs_specifiques = ?
            WHERE id = ?
            """, (
                type_vehicule,
                vehicule.marque,
                vehicule.modele,
                vehicule.annee,
                vehicule.kilometrage,
                vehicule.prix_achat,
                vehicule.cout_entretien_annuel,
                vehicule.categorie,
                attributs_json,
                vehicule.id
            ))

        # validation des changements
        self.conn.commit()

        return vehicule.id

    def charger_vehicule(self, vehicule_id):
        """
        charge un véhicule depuis la base de données

        args:
            vehicule_id (int): id du véhicule à charger

        returns:
            vehicule: objet véhicule correspondant, ou none si non trouvé
        """
        # récupération des données depuis la base
        self.cursor.execute('SELECT * FROM vehicules WHERE id = ?', (vehicule_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        # conversion du dictionnaire row en dictionnaire standard
        vehicule_data = dict(row)

        # désérialisation des attributs spécifiques
        attributs_specifiques = json.loads(vehicule_data['attributs_specifiques'])

        # import des classes nécessaires
        from model.vehicule import Voiture, Utilitaire, Moto

        # création de l'objet selon son type
        if vehicule_data['type'] == 'Voiture':
            return Voiture(
                id=vehicule_data['id'],
                marque=vehicule_data['marque'],
                modele=vehicule_data['modele'],
                annee=vehicule_data['annee'],
                kilometrage=vehicule_data['kilometrage'],
                prix_achat=vehicule_data['prix_achat'],
                cout_entretien_annuel=vehicule_data['cout_entretien_annuel'],
                nb_places=attributs_specifiques['nb_places'],
                puissance=attributs_specifiques['puissance'],
                carburant=attributs_specifiques['carburant'],
                options=attributs_specifiques['options']
            )
        elif vehicule_data['type'] == 'Utilitaire':
            return Utilitaire(
                id=vehicule_data['id'],
                marque=vehicule_data['marque'],
                modele=vehicule_data['modele'],
                annee=vehicule_data['annee'],
                kilometrage=vehicule_data['kilometrage'],
                prix_achat=vehicule_data['prix_achat'],
                cout_entretien_annuel=vehicule_data['cout_entretien_annuel'],
                volume=attributs_specifiques['volume'],
                charge_utile=attributs_specifiques['charge_utile'],
                hayon=attributs_specifiques['hayon']
            )
        elif vehicule_data['type'] == 'Moto':
            return Moto(
                id=vehicule_data['id'],
                marque=vehicule_data['marque'],
                modele=vehicule_data['modele'],
                annee=vehicule_data['annee'],
                kilometrage=vehicule_data['kilometrage'],
                prix_achat=vehicule_data['prix_achat'],
                cout_entretien_annuel=vehicule_data['cout_entretien_annuel'],
                cylindree=attributs_specifiques['cylindree'],
                type_moto=attributs_specifiques['type']
            )
        else:
            # type non reconnu
            return None

    def charger_tous_vehicules(self):
        """
        charge tous les véhicules depuis la base de données

        returns:
            list: liste des objets véhicule
        """
        # récupération de tous les véhicules
        self.cursor.execute('SELECT id FROM vehicules')
        rows = self.cursor.fetchall()

        vehicules = []
        for row in rows:
            vehicule = self.charger_vehicule(row['id'])
            if vehicule:
                vehicules.append(vehicule)

        return vehicules

    def supprimer_vehicule(self, vehicule_id):
        """
        supprime un véhicule de la base de données

        args:
            vehicule_id (int): id du véhicule à supprimer

        returns:
            bool: true si le véhicule a été supprimé, false sinon
        """
        try:
            # vérifier si le véhicule a des réservations
            self.cursor.execute('SELECT COUNT(*) FROM reservations WHERE vehicule_id = ?', (vehicule_id,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"impossible de supprimer un véhicule avec {count} réservations")
                return False

            # suppression du véhicule
            self.cursor.execute('DELETE FROM vehicules WHERE id = ?', (vehicule_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"erreur lors de la suppression du véhicule: {e}")
            return False

    def rechercher_vehicules(self, criteres=None):
        """
        recherche des véhicules selon certains critères

        args:
            criteres (dict, optional): critères de recherche

        returns:
            list: liste des véhicules correspondant aux critères
        """
        if criteres is None:
            return self.charger_tous_vehicules()

        # construction de la requête sql avec les critères
        query = 'SELECT id FROM vehicules WHERE 1=1'
        params = []

        # ajout des critères à la requête
        for cle, valeur in criteres.items():
            if cle in ['marque', 'modele', 'categorie', 'type']:
                query += f" AND {cle} = ?"
                params.append(valeur)
            elif cle == 'annee_min':
                query += " AND annee >= ?"
                params.append(valeur)
            elif cle == 'annee_max':
                query += " AND annee <= ?"
                params.append(valeur)
            elif cle == 'prix_max':
                query += " AND prix_achat <= ?"
                params.append(valeur)

        # exécution de la requête
        self.cursor.execute(query, params)

        # chargement de chaque véhicule trouvé
        vehicules = []
        for row in self.cursor.fetchall():
            vehicule = self.charger_vehicule(row['id'])
            if vehicule:
                vehicules.append(vehicule)

        return vehicules

    # méthodes pour les clients

    def sauvegarder_client(self, client):
        """
        sauvegarde un client dans la base de données

        args:
            client: objet de type client

        returns:
            int: id du client sauvegardé
        """
        if client.id is None:
            # création d'un nouveau client
            self.cursor.execute("""
            INSERT INTO clients (nom, prenom, adresse, telephone, email)
            VALUES (?, ?, ?, ?, ?)
            """, (
                client.nom,
                client.prenom,
                client.adresse,
                client.telephone,
                client.email
            ))

            # récupération de l'id généré
            client.id = self.cursor.lastrowid
        else:
            # mise à jour d'un client existant
            self.cursor.execute("""
            UPDATE clients
            SET nom = ?, prenom = ?, adresse = ?, telephone = ?, email = ?
            WHERE id = ?
            """, (
                client.nom,
                client.prenom,
                client.adresse,
                client.telephone,
                client.email,
                client.id
            ))

        # validation des changements
        self.conn.commit()

        return client.id

    def charger_client(self, client_id):
        """
        charge un client depuis la base de données

        args:
            client_id (int): id du client à charger

        returns:
            client: objet client correspondant, ou none si non trouvé
        """
        # récupération des données depuis la base
        self.cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        # import de la classe client
        from model.client import Client

        # création de l'objet client
        client = Client(
            id=row['id'],
            nom=row['nom'],
            prenom=row['prenom'],
            adresse=row['adresse'],
            telephone=row['telephone'],
            email=row['email']
        )

        # chargement des réservations du client
        client.historique_reservations = self.charger_reservations_client(client_id)

        return client

    def charger_tous_clients(self):
        """
        charge tous les clients depuis la base de données

        returns:
            list: liste des objets client
        """
        # récupération de tous les clients
        self.cursor.execute('SELECT id FROM clients')
        rows = self.cursor.fetchall()

        clients = []
        for row in rows:
            client = self.charger_client(row['id'])
            if client:
                clients.append(client)

        return clients

    def supprimer_client(self, client_id):
        """
        supprime un client de la base de données

        args:
            client_id (int): id du client à supprimer

        returns:
            bool: true si suppression réussie, false sinon
        """
        try:
            # vérifier si le client a des réservations
            self.cursor.execute('SELECT COUNT(*) FROM reservations WHERE client_id = ?', (client_id,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"impossible de supprimer un client avec {count} réservations")
                return False

            # suppression du client
            self.cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"erreur lors de la suppression du client: {e}")
            return False

    def rechercher_clients(self, criteres=None):
        """
        recherche des clients selon certains critères

        args:
            criteres (dict, optional): critères de recherche

        returns:
            list: liste des clients correspondant aux critères
        """
        # construction de la requête sql
        query = 'SELECT id FROM clients WHERE 1=1'
        params = []

        if criteres:
            for cle, valeur in criteres.items():
                if cle in ['nom', 'prenom', 'email', 'telephone']:
                    query += f" AND {cle} LIKE ?"
                    params.append(f"%{valeur}%")

        # exécution de la requête
        self.cursor.execute(query, params)

        # chargement de chaque client trouvé
        clients = []
        for row in self.cursor.fetchall():
            client = self.charger_client(row['id'])
            if client:
                clients.append(client)

        return clients

    # méthodes pour les réservations

    def sauvegarder_reservation(self, reservation):
        """
        sauvegarde une réservation dans la base de données

        args:
            reservation: objet de type reservation

        returns:
            int: id de la réservation sauvegardée
        """
        # formatage des dates pour sqlite
        date_debut_str = reservation.date_debut.strftime('%Y-%m-%d %H:%M:%S')
        date_fin_str = reservation.date_fin.strftime('%Y-%m-%d %H:%M:%S')

        if reservation.id is None:
            # création d'une nouvelle réservation
            self.cursor.execute("""
            INSERT INTO reservations (client_id, vehicule_id, date_debut, date_fin, prix_total, statut)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reservation.client_id,
                reservation.vehicule_id,
                date_debut_str,
                date_fin_str,
                reservation.prix_total,
                reservation.statut
            ))

            # récupération de l'id généré
            reservation.id = self.cursor.lastrowid
        else:
            # mise à jour d'une réservation existante
            self.cursor.execute("""
            UPDATE reservations
            SET client_id = ?, vehicule_id = ?, date_debut = ?, date_fin = ?, prix_total = ?, statut = ?
            WHERE id = ?
            """, (
                reservation.client_id,
                reservation.vehicule_id,
                date_debut_str,
                date_fin_str,
                reservation.prix_total,
                reservation.statut,
                reservation.id
            ))

        # validation des changements
        self.conn.commit()

        return reservation.id

    def charger_reservation(self, reservation_id):
        """
        charge une réservation depuis la base de données

        args:
            reservation_id (int): id de la réservation à charger

        returns:
            reservation: objet réservation correspondant, ou none si non trouvé
        """
        # récupération des données depuis la base
        self.cursor.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        # import de la classe reservation
        from model.reservation import Reservation

        # conversion des dates de string à datetime
        date_debut = datetime.strptime(row['date_debut'], '%Y-%m-%d %H:%M:%S')
        date_fin = datetime.strptime(row['date_fin'], '%Y-%m-%d %H:%M:%S')

        # création de l'objet réservation
        reservation = Reservation(
            id=row['id'],
            client_id=row['client_id'],
            vehicule_id=row['vehicule_id'],
            date_debut=date_debut,
            date_fin=date_fin,
            prix_total=row['prix_total'],
            statut=row['statut']
        )

        return reservation

    def charger_reservations_client(self, client_id):
        """
        charge toutes les réservations d'un client

        args:
            client_id (int): id du client

        returns:
            list: liste des réservations du client
        """
        # récupération des ids de réservation
        self.cursor.execute('SELECT id FROM reservations WHERE client_id = ?', (client_id,))
        rows = self.cursor.fetchall()

        # chargement de chaque réservation
        reservations = []
        for row in rows:
            reservation = self.charger_reservation(row['id'])
            if reservation:
                reservations.append(reservation)

        return reservations

    def charger_reservations_vehicule(self, vehicule_id, date_debut=None, date_fin=None):
        """
        charge les réservations d'un véhicule, éventuellement filtrées par période

        args:
            vehicule_id (int): id du véhicule
            date_debut (datetime, optional): date de début de la période
            date_fin (datetime, optional): date de fin de la période

        returns:
            list: liste des réservations du véhicule
        """
        # construction de la requête sql
        query = 'SELECT id FROM reservations WHERE vehicule_id = ?'
        params = [vehicule_id]

        if date_debut:
            query += ' AND date_fin >= ?'
            params.append(date_debut.strftime('%Y-%m-%d %H:%M:%S'))

        if date_fin:
            query += ' AND date_debut <= ?'
            params.append(date_fin.strftime('%Y-%m-%d %H:%M:%S'))

        # exécution de la requête
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # chargement de chaque réservation
        reservations = []
        for row in rows:
            reservation = self.charger_reservation(row['id'])
            if reservation:
                reservations.append(reservation)

        return reservations

    def supprimer_reservation(self, reservation_id):
        """
        supprime une réservation de la base de données

        args:
            reservation_id (int): id de la réservation à supprimer

        returns:
            bool: true si suppression réussie, false sinon
        """
        try:
            # vérifier si la réservation a une facture
            self.cursor.execute('SELECT COUNT(*) FROM factures WHERE reservation_id = ?', (reservation_id,))
            count = self.cursor.fetchone()[0]
            if count > 0:
                print(f"impossible de supprimer une réservation avec {count} factures")
                return False

            # suppression de la réservation
            self.cursor.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"erreur lors de la suppression de la réservation: {e}")
            return False

    # méthodes pour les factures

    def sauvegarder_facture(self, facture):
        """
        sauvegarde une facture dans la base de données

        args:
            facture: objet de type facture

        returns:
            int: id de la facture sauvegardée
        """
        # formatage de la date pour sqlite
        date_emission_str = facture.date_emission.strftime('%Y-%m-%d %H:%M:%S')

        if facture.id is None:
            # création d'une nouvelle facture
            self.cursor.execute("""
            INSERT INTO factures (reservation_id, date_emission, montant_ht, taux_tva, montant_ttc)
            VALUES (?, ?, ?, ?, ?)
            """, (
                facture.reservation_id,
                date_emission_str,
                facture.montant_ht,
                facture.taux_tva,
                facture.montant_ttc
            ))

            # récupération de l'id généré
            facture.id = self.cursor.lastrowid
        else:
            # mise à jour d'une facture existante
            self.cursor.execute("""
            UPDATE factures
            SET reservation_id = ?, date_emission = ?, montant_ht = ?, taux_tva = ?, montant_ttc = ?
            WHERE id = ?
            """, (
                facture.reservation_id,
                date_emission_str,
                facture.montant_ht,
                facture.taux_tva,
                facture.montant_ttc,
                facture.id
            ))

        # validation des changements
        self.conn.commit()

        return facture.id

    def charger_facture(self, facture_id):
        """
        charge une facture depuis la base de données

        args:
            facture_id (int): id de la facture à charger

        returns:
            facture: objet facture correspondant, ou none si non trouvé
        """
        # récupération des données depuis la base
        self.cursor.execute('SELECT * FROM factures WHERE id = ?', (facture_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        # import de la classe facture
        from model.facture import Facture

        # conversion de la date de string à datetime
        date_emission = datetime.strptime(row['date_emission'], '%Y-%m-%d %H:%M:%S')

        # création de l'objet facture
        facture = Facture(
            id=row['id'],
            reservation_id=row['reservation_id'],
            date_emission=date_emission,
            montant_ht=row['montant_ht'],
            taux_tva=row['taux_tva'],
            montant_ttc=row['montant_ttc']
        )

        return facture

    def charger_facture_par_reservation(self, reservation_id):
        """
        charge la facture associée à une réservation

        args:
            reservation_id (int): id de la réservation

        returns:
            facture: objet facture correspondant, ou none si non trouvé
        """
        # récupération de l'id de facture
        self.cursor.execute('SELECT id FROM factures WHERE reservation_id = ?', (reservation_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return self.charger_facture(row['id'])

    def charger_toutes_factures(self):
        """
        charge toutes les factures depuis la base de données

        returns:
            list: liste des objets facture
        """
        # récupération de toutes les factures
        self.cursor.execute('SELECT id FROM factures')
        rows = self.cursor.fetchall()

        factures = []
        for row in rows:
            facture = self.charger_facture(row['id'])
            if facture:
                factures.append(facture)

        return factures

    def supprimer_facture(self, facture_id):
        """
        supprime une facture de la base de données

        args:
            facture_id (int): id de la facture à supprimer

        returns:
            bool: true si suppression réussie, false sinon
        """
        try:
            self.cursor.execute('DELETE FROM factures WHERE id = ?', (facture_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"erreur lors de la suppression de la facture: {e}")
            return False

    # méthodes utilitaires

    def generer_donnees_test(self, nb_voitures=5, nb_utilitaires=3, nb_motos=2, nb_clients=4):
        """
        génère des données de test

        args:
            nb_voitures (int): nombre de voitures à générer
            nb_utilitaires (int): nombre d'utilitaires à générer
            nb_motos (int): nombre de motos à générer
            nb_clients (int): nombre de clients à générer
        """
        import random
        from model.vehicule import Voiture, Utilitaire, Moto
        from model.client import Client
        from model.reservation import Reservation
        from datetime import timedelta

        # listes de valeurs pour la génération aléatoire
        marques_voiture = ["Renault", "Peugeot", "Citroën", "Toyota", "Volkswagen", "Ford"]
        modeles_voiture = {
            "Renault": ["Clio", "Megane", "Captur"],
            "Peugeot": ["208", "308", "3008"],
            "Citroën": ["C3", "C4", "Berlingo"],
            "Toyota": ["Yaris", "Corolla", "RAV4"],
            "Volkswagen": ["Polo", "Golf", "Tiguan"],
            "Ford": ["Fiesta", "Focus", "Kuga"]
        }

        marques_utilitaire = ["Renault", "Citroën", "Fiat", "Mercedes"]
        modeles_utilitaire = {
            "Renault": ["Kangoo", "Trafic", "Master"],
            "Citroën": ["Berlingo", "Jumpy", "Jumper"],
            "Fiat": ["Doblo", "Ducato"],
            "Mercedes": ["Citan", "Vito", "Sprinter"]
        }

        marques_moto = ["Honda", "Yamaha", "Kawasaki", "Suzuki", "BMW"]
        modeles_moto = {
            "Honda": ["CB500F", "CBR650R", "Africa Twin"],
            "Yamaha": ["MT-07", "MT-09", "Tracer 900"],
            "Kawasaki": ["Z650", "Z900", "Ninja 650"],
            "Suzuki": ["SV650", "GSX-S750", "V-Strom"],
            "BMW": ["G310R", "F900R", "R1250GS"]
        }

        types_moto = ["Roadster", "Sportive", "Trail", "Routière"]
        carburants = ["Essence", "Diesel", "Hybride", "Électrique"]
        options = ["Climatisation", "GPS", "Bluetooth", "Régulateur", "Caméra recul", "Toit ouvrant",
                   "Sièges chauffants"]
        noms = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent"]
        prenoms = ["Jean", "Pierre", "Michel", "André", "Philippe", "René", "Louis", "Alain", "Jacques", "François",
                   "Marie", "Nathalie", "Isabelle", "Sylvie", "Catherine", "Monique", "Françoise", "Nicole",
                   "Jacqueline", "Martine"]
        villes = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux",
                  "Lille"]

        print("génération des données de test en cours...")

        # génération des véhicules
        vehicules_ids = []

        # création des voitures
        for i in range(nb_voitures):
            marque = random.choice(marques_voiture)
            modele = random.choice(modeles_voiture[marque])
            annee = random.randint(2015, 2023)
            kilometrage = random.randint(0, 100000)
            prix_achat = random.randint(10000, 35000)
            cout_entretien = random.randint(500, 2000)

            # attributs spécifiques pour les voitures
            nb_places = random.randint(2, 7)
            puissance = random.randint(70, 250)
            carburant = random.choice(carburants)
            nb_options = random.randint(0, 4)
            options_voiture = random.sample(options, nb_options)

            voiture = Voiture(
                id=None,
                marque=marque,
                modele=modele,
                annee=annee,
                kilometrage=kilometrage,
                prix_achat=prix_achat,
                cout_entretien_annuel=cout_entretien,
                nb_places=nb_places,
                puissance=puissance,
                carburant=carburant,
                options=options_voiture
            )

            voiture_id = self.sauvegarder_vehicule(voiture)
            vehicules_ids.append(voiture_id)

        # création des utilitaires
        for i in range(nb_utilitaires):
            marque = random.choice(marques_utilitaire)
            modele = random.choice(modeles_utilitaire[marque])
            annee = random.randint(2015, 2023)
            kilometrage = random.randint(0, 150000)
            prix_achat = random.randint(15000, 40000)
            cout_entretien = random.randint(800, 2500)

            # attributs spécifiques pour les utilitaires
            volume = round(random.uniform(3.0, 20.0), 1)
            charge_utile = random.randint(500, 2000)
            hayon = random.choice([True, False])

            utilitaire = Utilitaire(
                id=None,
                marque=marque,
                modele=modele,
                annee=annee,
                kilometrage=kilometrage,
                prix_achat=prix_achat,
                cout_entretien_annuel=cout_entretien,
                volume=volume,
                charge_utile=charge_utile,
                hayon=hayon
            )

            utilitaire_id = self.sauvegarder_vehicule(utilitaire)
            vehicules_ids.append(utilitaire_id)

        # création des motos
        for i in range(nb_motos):
            marque = random.choice(marques_moto)
            modele = random.choice(modeles_moto[marque])
            annee = random.randint(2015, 2023)
            kilometrage = random.randint(0, 50000)
            prix_achat = random.randint(5000, 25000)
            cout_entretien = random.randint(300, 1500)

            # attributs spécifiques pour les motos
            cylindree = random.choice([125, 300, 500, 650, 750, 900, 1000, 1200])
            type_moto = random.choice(types_moto)

            moto = Moto(
                id=None,
                marque=marque,
                modele=modele,
                annee=annee,
                kilometrage=kilometrage,
                prix_achat=prix_achat,
                cout_entretien_annuel=cout_entretien,
                cylindree=cylindree,
                type_moto=type_moto
            )

            moto_id = self.sauvegarder_vehicule(moto)
            vehicules_ids.append(moto_id)

        # création des clients
        clients_ids = []
        for i in range(nb_clients):
            nom = random.choice(noms)
            prenom = random.choice(prenoms)
            ville = random.choice(villes)
            adresse = f"{random.randint(1, 100)} rue {random.choice(['de la Paix', 'Victor Hugo', 'des Lilas', 'Principale'])}, {random.randint(10000, 99999)} {ville}"
            telephone = f"0{random.randint(1, 9)}{random.randint(10000000, 99999999)}"
            email = f"{prenom.lower()}.{nom.lower()}@example.com"

            client = Client(
                id=None,
                nom=nom,
                prenom=prenom,
                adresse=adresse,
                telephone=telephone,
                email=email
            )

            client_id = self.sauvegarder_client(client)
            clients_ids.append(client_id)

        # création des réservations
        maintenant = datetime.now()
        reservations_ids = []
        for i in range(min(len(clients_ids) * 2, len(vehicules_ids) * 2)):
            client_id = random.choice(clients_ids)
            vehicule_id = random.choice(vehicules_ids)

            # dates aléatoires sur les 3 derniers mois et les 3 prochains mois
            jours_avant_debut = random.randint(-90, 60)
            duree_location = random.randint(1, 14)

            date_debut = maintenant + timedelta(days=jours_avant_debut)
            date_fin = date_debut + timedelta(days=duree_location)

            # prix aléatoire entre 20 et 100€ par jour
            prix_journalier = random.randint(20, 100)
            prix_total = prix_journalier * duree_location

            # statut basé sur les dates
            if date_fin < maintenant:
                statut = "terminée"
            elif date_debut < maintenant:
                statut = "confirmée"
            else:
                statut = "confirmée"

            reservation = Reservation(
                id=None,
                client_id=client_id,
                vehicule_id=vehicule_id,
                date_debut=date_debut,
                date_fin=date_fin,
                prix_total=prix_total,
                statut=statut
            )

            reservation_id = self.sauvegarder_reservation(reservation)
            reservations_ids.append(reservation_id)

            # créer une facture pour les réservations terminées
            if statut == "terminée":
                from model.facture import Facture

                facture = Facture(
                    id=None,
                    reservation_id=reservation_id,
                    date_emission=date_fin + timedelta(days=1),
                    montant_ht=prix_total / 1.2,  # TVA 20%
                    taux_tva=0.2,
                )

                self.sauvegarder_facture(facture)

        print(
            f"données de test générées avec succès: {nb_voitures} voitures, {nb_utilitaires} utilitaires, {nb_motos} motos, {nb_clients} clients et {len(reservations_ids)} réservations")

    # documentation des tests
    """
    tests unitaires pour ce module :

    le fichier tests/test_database.py contient les tests unitaires pour ce module.
    les tests vérifient :
    - la création correcte des tables dans la base de données
    - les opérations crud (create, read, update, delete) pour chaque entité
    - la persistance et la récupération des données
    - la conversion entre objets python et représentation en base de données
    - la gestion des relations entre entités

    pour exécuter ces tests, utiliser la commande:
    python -m unittest tests.test_database
    """

# exemple d'utilisation (ce code ne s'exécute que si on lance le fichier directement)
if __name__ == "__main__":
    # création d'une instance de la base de données
    db = Database("test.db")
    print("base de données initialisée avec succès!")

    # génération de données de test
    db.generer_donnees_test()

    # fermeture de la connexion
    db.fermer()