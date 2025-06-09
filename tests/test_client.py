# tests/test_client.py
# Tests unitaires pour la classe Client
# Vérifie la gestion des réservations, calculs de montants et statut de fidélité

import unittest
import sys
import os
from datetime import datetime, timedelta

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.client import Client


class ReservationMock:
    """Classe mock pour simuler une réservation dans les tests"""

    def __init__(self, prix_total, statut):
        self.prix_total = prix_total
        self.statut = statut


class TestClient(unittest.TestCase):

    def setUp(self):
        """Préparation des objets de test"""
        self.client = Client(
            id=1,
            nom="Dupont",
            prenom="Jean",
            adresse="123 rue de la Paix, Paris",
            telephone="01 23 45 67 89",
            email="jean.dupont@example.com"
        )

    def test_creation_client(self):
        """Test de la création d'un client"""
        self.assertEqual(self.client.nom, "Dupont")
        self.assertEqual(self.client.prenom, "Jean")
        self.assertEqual(len(self.client.historique_reservations), 0)

    def test_ajout_reservation(self):
        """Test de l'ajout d'une réservation à l'historique"""
        reservation = ReservationMock(150.0, "confirmée")
        self.client.ajouter_reservation(reservation)
        self.assertEqual(len(self.client.historique_reservations), 1)
        self.assertIn(reservation, self.client.historique_reservations)

    def test_reservations_en_cours(self):
        """Test de récupération des réservations en cours"""
        resa1 = ReservationMock(100.0, "confirmée")
        resa2 = ReservationMock(200.0, "terminée")
        resa3 = ReservationMock(150.0, "confirmée")

        self.client.ajouter_reservation(resa1)
        self.client.ajouter_reservation(resa2)
        self.client.ajouter_reservation(resa3)

        en_cours = self.client.obtenir_reservations_en_cours()
        self.assertEqual(len(en_cours), 2)
        self.assertIn(resa1, en_cours)
        self.assertIn(resa3, en_cours)

    def test_reservations_passees(self):
        """Test de récupération des réservations terminées"""
        resa1 = ReservationMock(100.0, "confirmée")
        resa2 = ReservationMock(200.0, "terminée")
        resa3 = ReservationMock(300.0, "terminée")

        self.client.ajouter_reservation(resa1)
        self.client.ajouter_reservation(resa2)
        self.client.ajouter_reservation(resa3)

        passees = self.client.obtenir_reservations_passees()
        self.assertEqual(len(passees), 2)
        self.assertEqual(passees[0].prix_total, 200.0)
        self.assertEqual(passees[1].prix_total, 300.0)

    def test_calcul_montant_total(self):
        """Test du calcul du montant total dépensé"""
        resa1 = ReservationMock(150.0, "terminée")
        resa2 = ReservationMock(250.0, "terminée")
        resa3 = ReservationMock(100.0, "confirmée")  # Non comptée

        self.client.ajouter_reservation(resa1)
        self.client.ajouter_reservation(resa2)
        self.client.ajouter_reservation(resa3)

        total = self.client.calculer_montant_total_depense()
        self.assertEqual(total, 400.0)

    def test_client_fidele_vrai(self):
        """Test du statut de client fidèle (cas positif)"""
        # Ajout de 6 réservations (seuil par défaut = 5)
        for i in range(6):
            resa = ReservationMock(100.0, "terminée")
            self.client.ajouter_reservation(resa)

        self.assertTrue(self.client.est_client_fidele())

    def test_client_fidele_faux(self):
        """Test du statut de client fidèle (cas négatif)"""
        # Ajout de 3 réservations seulement
        for i in range(3):
            resa = ReservationMock(100.0, "terminée")
            self.client.ajouter_reservation(resa)

        self.assertFalse(self.client.est_client_fidele())

    def test_mise_a_jour_coordonnees(self):
        """Test de la mise à jour des coordonnées"""
        ancien_email = self.client.email
        nouveau_telephone = "06 12 34 56 78"

        self.client.mettre_a_jour_coordonnees(
            telephone=nouveau_telephone,
            email="nouveau@example.com"
        )

        self.assertEqual(self.client.telephone, nouveau_telephone)
        self.assertEqual(self.client.email, "nouveau@example.com")
        # L'adresse ne doit pas avoir changé
        self.assertEqual(self.client.adresse, "123 rue de la Paix, Paris")


if __name__ == '__main__':
    unittest.main()