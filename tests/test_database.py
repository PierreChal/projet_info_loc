# tests/test_database.py
# Tests unitaires pour la classe Database
# Vérifie les opérations CRUD et la persistance des données

import unittest
import sys
import os
import tempfile
from datetime import datetime, timedelta

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import Database
from model.vehicule import Voiture
from model.client import Client
from model.reservation import Reservation


class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Préparation d'une base de données temporaire pour les tests"""
        # Création d'un fichier temporaire pour la base de données
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()

        self.db = Database(self.temp_db.name)

        # Objets de test
        self.voiture_test = Voiture(
            id=None,  # Sera assigné par la DB
            marque="Toyota",
            modele="Corolla",
            annee=2021,
            kilometrage=10000,
            prix_achat=20000,
            cout_entretien_annuel=700,
            nb_places=5,
            puissance=120,
            carburant="Hybride",
            options=["GPS", "Climatisation"]
        )

        self.client_test = Client(
            id=None,
            nom="Martin",
            prenom="Sophie",
            adresse="456 avenue des Tests, 75001 Paris",
            telephone="01 98 76 54 32",
            email="sophie.martin@test.com"
        )

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.db.fermer()
        os.unlink(self.temp_db.name)

    def test_creation_tables(self):
        """Test de la création des tables"""
        # Vérification que les tables existent
        cursor = self.db.cursor
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['vehicules', 'clients', 'reservations', 'factures']
        for table in expected_tables:
            self.assertIn(table, tables)

    def test_sauvegarde_et_chargement_vehicule(self):
        """Test de sauvegarde et chargement d'un véhicule"""
        # Sauvegarde
        vehicule_id = self.db.sauvegarder_vehicule(self.voiture_test)
        self.assertIsNotNone(vehicule_id)
        self.assertEqual(self.voiture_test.id, vehicule_id)

        # Chargement
        vehicule_charge = self.db.charger_vehicule(vehicule_id)
        self.assertIsNotNone(vehicule_charge)
        self.assertEqual(vehicule_charge.marque, "Toyota")
        self.assertEqual(vehicule_charge.modele, "Corolla")
        self.assertEqual(vehicule_charge.carburant, "Hybride")
        self.assertEqual(len(vehicule_charge.options), 2)

    def test_mise_a_jour_vehicule(self):
        """Test de mise à jour d'un véhicule existant"""
        # Sauvegarde initiale
        vehicule_id = self.db.sauvegarder_vehicule(self.voiture_test)

        # Modification
        self.voiture_test.kilometrage = 15000
        self.voiture_test.options.append("Bluetooth")

        # Mise à jour
        self.db.sauvegarder_vehicule(self.voiture_test)

        # Vérification
        vehicule_charge = self.db.charger_vehicule(vehicule_id)
        self.assertEqual(vehicule_charge.kilometrage, 15000)
        self.assertIn("Bluetooth", vehicule_charge.options)

    def test_sauvegarde_et_chargement_client(self):
        """Test de sauvegarde et chargement d'un client"""
        # Sauvegarde
        client_id = self.db.sauvegarder_client(self.client_test)
        self.assertIsNotNone(client_id)

        # Chargement
        client_charge = self.db.charger_client(client_id)
        self.assertIsNotNone(client_charge)
        self.assertEqual(client_charge.nom, "Martin")
        self.assertEqual(client_charge.prenom, "Sophie")
        self.assertEqual(client_charge.email, "sophie.martin@test.com")

    def test_sauvegarde_et_chargement_reservation(self):
        """Test de sauvegarde et chargement d'une réservation"""
        # Préparation : créer véhicule et client
        vehicule_id = self.db.sauvegarder_vehicule(self.voiture_test)
        client_id = self.db.sauvegarder_client(self.client_test)

        # Création de la réservation
        reservation = Reservation(
            id=None,
            client_id=client_id,
            vehicule_id=vehicule_id,
            date_debut=datetime.now() + timedelta(days=1),
            date_fin=datetime.now() + timedelta(days=5),
            prix_total=300.0,
            statut="confirmée"
        )

        # Sauvegarde
        reservation_id = self.db.sauvegarder_reservation(reservation)
        self.assertIsNotNone(reservation_id)

        # Chargement
        reservation_chargee = self.db.charger_reservation(reservation_id)
        self.assertIsNotNone(reservation_chargee)
        self.assertEqual(reservation_chargee.client_id, client_id)
        self.assertEqual(reservation_chargee.vehicule_id, vehicule_id)
        self.assertEqual(reservation_chargee.prix_total, 300.0)

    def test_chargement_tous_vehicules(self):
        """Test de chargement de tous les véhicules"""
        # Ajout de plusieurs véhicules
        vehicule2 = Voiture(
            id=None, marque="Honda", modele="Civic", annee=2020,
            kilometrage=20000, prix_achat=18000, cout_entretien_annuel=600,
            nb_places=5, puissance=100, carburant="Essence", options=[]
        )

        self.db.sauvegarder_vehicule(self.voiture_test)
        self.db.sauvegarder_vehicule(vehicule2)

        # Chargement de tous
        tous_vehicules = self.db.charger_tous_vehicules()
        self.assertEqual(len(tous_vehicules), 2)

        marques = [v.marque for v in tous_vehicules]
        self.assertIn("Toyota", marques)
        self.assertIn("Honda", marques)

    def test_recherche_vehicules_par_criteres(self):
        """Test de recherche de véhicules par critères"""
        # Ajout de véhicules variés
        vehicule2 = Voiture(
            id=None, marque="Honda", modele="Civic", annee=2018,
            kilometrage=40000, prix_achat=15000, cout_entretien_annuel=500,
            nb_places=5, puissance=110, carburant="Essence", options=[]
        )

        self.db.sauvegarder_vehicule(self.voiture_test)  # Toyota 2021
        self.db.sauvegarder_vehicule(vehicule2)  # Honda 2018

        # Recherche par marque
        toyotas = self.db.rechercher_vehicules({"marque": "Toyota"})
        self.assertEqual(len(toyotas), 1)
        self.assertEqual(toyotas[0].marque, "Toyota")

        # Recherche par année minimum
        recents = self.db.rechercher_vehicules({"annee_min": 2020})
        self.assertEqual(len(recents), 1)
        self.assertEqual(recents[0].annee, 2021)

    def test_suppression_vehicule_sans_reservation(self):
        """Test de suppression d'un véhicule sans réservation"""
        vehicule_id = self.db.sauvegarder_vehicule(self.voiture_test)

        # Suppression
        resultat = self.db.supprimer_vehicule(vehicule_id)
        self.assertTrue(resultat)

        # Vérification
        vehicule_supprime = self.db.charger_vehicule(vehicule_id)
        self.assertIsNone(vehicule_supprime)

    def test_suppression_vehicule_avec_reservation(self):
        """Test de suppression d'un véhicule avec réservation (doit échouer)"""
        vehicule_id = self.db.sauvegarder_vehicule(self.voiture_test)
        client_id = self.db.sauvegarder_client(self.client_test)

        # Création d'une réservation
        reservation = Reservation(
            id=None, client_id=client_id, vehicule_id=vehicule_id,
            date_debut=datetime.now() + timedelta(days=1),
            date_fin=datetime.now() + timedelta(days=3),
            prix_total=150.0
        )
        self.db.sauvegarder_reservation(reservation)

        # Tentative de suppression (doit échouer)
        resultat = self.db.supprimer_vehicule(vehicule_id)
        self.assertFalse(resultat)

    def test_chargement_reservations_client(self):
        """Test de chargement des réservations d'un client"""
        vehicule_id = self.db.sauvegarder_vehicule(self.voiture_test)
        client_id = self.db.sauvegarder_client(self.client_test)

        # Création de plusieurs réservations
        for i in range(3):
            reservation = Reservation(
                id=None, client_id=client_id, vehicule_id=vehicule_id,
                date_debut=datetime.now() + timedelta(days=i * 7),
                date_fin=datetime.now() + timedelta(days=i * 7 + 3),
                prix_total=100.0 + i * 50
            )
            self.db.sauvegarder_reservation(reservation)

        # Chargement des réservations du client
        reservations = self.db.charger_reservations_client(client_id)
        self.assertEqual(len(reservations), 3)


if __name__ == '__main__':
    unittest.main()