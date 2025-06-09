# tests/test_reservation.py
# Tests unitaires pour la classe Reservation
# Vérifie les calculs de prix, durées, changements de statut et validations

import unittest
import sys
import os
from datetime import datetime, timedelta

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.reservation import Reservation


class VehiculeMock:
    """Classe mock pour simuler un véhicule dans les tests"""

    def __init__(self, tarif_journalier=50.0):
        self.tarif_journalier = tarif_journalier

    def calculer_tarif_journalier(self):
        return self.tarif_journalier


class TestReservation(unittest.TestCase):

    def setUp(self):
        """Préparation des objets de test"""
        self.aujourd_hui = datetime.now()
        self.demain = self.aujourd_hui + timedelta(days=1)
        self.dans_5_jours = self.aujourd_hui + timedelta(days=5)

        self.reservation = Reservation(
            id=1,
            client_id=101,
            vehicule_id=201,
            date_debut=self.demain,
            date_fin=self.dans_5_jours,
            prix_total=200.0
        )

        self.vehicule_mock = VehiculeMock(50.0)

    def test_creation_reservation_valide(self):
        """Test de création d'une réservation valide"""
        self.assertEqual(self.reservation.client_id, 101)
        self.assertEqual(self.reservation.vehicule_id, 201)
        self.assertEqual(self.reservation.statut, "confirmée")

    def test_creation_dates_invalides(self):
        """Test de création avec dates invalides (doit échouer)"""
        with self.assertRaises(ValueError):
            Reservation(
                id=2,
                client_id=101,
                vehicule_id=201,
                date_debut=self.dans_5_jours,  # Après la fin !
                date_fin=self.demain,
                prix_total=200.0
            )

    def test_calcul_duree_jours(self):
        """Test du calcul de la durée en jours"""
        duree = self.reservation.calculer_duree_jours()
        self.assertEqual(duree, 4)  # Du jour 1 au jour 5 = 4 jours

    def test_calcul_prix_courte_duree(self):
        """Test du calcul de prix pour une courte durée (sans réduction)"""
        # Réservation de 3 jours
        reservation_courte = Reservation(
            id=2,
            client_id=101,
            vehicule_id=201,
            date_debut=self.demain,
            date_fin=self.demain + timedelta(days=3)
        )

        prix = reservation_courte.calculer_prix(self.vehicule_mock)
        expected = 50.0 * 3  # 3 jours × 50€, pas de réduction
        self.assertEqual(prix, expected)

    def test_calcul_prix_avec_reduction_semaine(self):
        """Test du calcul de prix avec réduction semaine (10%)"""
        # Réservation de 8 jours
        reservation_semaine = Reservation(
            id=3,
            client_id=101,
            vehicule_id=201,
            date_debut=self.demain,
            date_fin=self.demain + timedelta(days=8)
        )

        prix = reservation_semaine.calculer_prix(self.vehicule_mock)
        expected = (50.0 * 8) * 0.9  # 8 jours × 50€ × 10% réduction
        self.assertEqual(prix, expected)

    def test_calcul_prix_avec_reduction_mois(self):
        """Test du calcul de prix avec réduction mois (20%)"""
        # Réservation de 35 jours
        reservation_mois = Reservation(
            id=4,
            client_id=101,
            vehicule_id=201,
            date_debut=self.demain,
            date_fin=self.demain + timedelta(days=35)
        )

        prix = reservation_mois.calculer_prix(self.vehicule_mock)
        expected = (50.0 * 35) * 0.8  # 35 jours × 50€ × 20% réduction
        self.assertEqual(prix, expected)

    def test_annulation_reservation(self):
        """Test de l'annulation d'une réservation"""
        # Initialement confirmée
        self.assertEqual(self.reservation.statut, "confirmée")

        # Annulation réussie
        resultat = self.reservation.annuler()
        self.assertTrue(resultat)
        self.assertEqual(self.reservation.statut, "annulée")

        # Tentative d'annulation d'une réservation déjà annulée (doit échouer)
        resultat2 = self.reservation.annuler()
        self.assertFalse(resultat2)

    def test_terminaison_reservation(self):
        """Test de la terminaison d'une réservation"""
        resultat = self.reservation.terminer()
        self.assertTrue(resultat)
        self.assertEqual(self.reservation.statut, "terminée")

    def test_conflit_reservations(self):
        """Test de détection de conflit entre réservations"""
        # Réservation qui chevauche
        reservation_conflit = Reservation(
            id=2,
            client_id=102,
            vehicule_id=201,  # Même véhicule !
            date_debut=self.demain + timedelta(days=2),
            date_fin=self.demain + timedelta(days=7)
        )

        conflit = self.reservation.est_en_conflit_avec(reservation_conflit)
        self.assertTrue(conflit)

    def test_pas_de_conflit_vehicules_differents(self):
        """Test d'absence de conflit avec véhicules différents"""
        reservation_autre_vehicule = Reservation(
            id=2,
            client_id=102,
            vehicule_id=999,  # Véhicule différent
            date_debut=self.demain + timedelta(days=2),
            date_fin=self.demain + timedelta(days=7)
        )

        conflit = self.reservation.est_en_conflit_avec(reservation_autre_vehicule)
        self.assertFalse(conflit)

    def test_duree_en_jours_legacy(self):
        """Test de la méthode duree_en_jours (compatibilité)"""
        duree = self.reservation.duree_en_jours()
        self.assertEqual(duree, 5)  # +1 car on compte le jour de début et fin


if __name__ == '__main__':
    unittest.main()