# tests/test_parc.py
# Tests unitaires pour la classe Parc
# Vérifie la gestion des véhicules, disponibilités et fonction récursive

import unittest
import sys
import os
from datetime import datetime, timedelta

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.parc import Parc
from model.vehicule import Voiture
from model.reservation import Reservation


class TestParc(unittest.TestCase):

    def setUp(self):
        """Préparation des objets de test"""
        self.parc = Parc()

        # Création de véhicules de test
        self.voiture1 = Voiture(
            id=1, marque="Renault", modele="Clio", annee=2020,
            kilometrage=15000, prix_achat=15000, cout_entretien_annuel=600,
            nb_places=5, puissance=90, carburant="Essence", options=[]
        )

        self.voiture2 = Voiture(
            id=2, marque="Peugeot", modele="308", annee=2019,
            kilometrage=25000, prix_achat=18000, cout_entretien_annuel=800,
            nb_places=5, puissance=130, carburant="Diesel", options=[]
        )

        # Dates pour les tests
        self.aujourd_hui = datetime.now()
        self.demain = self.aujourd_hui + timedelta(days=1)
        self.dans_5_jours = self.aujourd_hui + timedelta(days=5)

    def test_ajout_vehicule(self):
        """Test de l'ajout d'un véhicule au parc"""
        initial_count = len(self.parc.vehicules)
        resultat = self.parc.ajouter_vehicule(self.voiture1)

        self.assertTrue(resultat)
        self.assertEqual(len(self.parc.vehicules), initial_count + 1)
        self.assertIn(self.voiture1, self.parc.vehicules)

    def test_ajout_vehicule_duplique(self):
        """Test d'ajout d'un véhicule déjà présent (doit échouer)"""
        self.parc.ajouter_vehicule(self.voiture1)
        resultat = self.parc.ajouter_vehicule(self.voiture1)  # Même véhicule

        self.assertFalse(resultat)
        self.assertEqual(len(self.parc.vehicules), 1)  # Pas de doublon

    def test_retrait_vehicule_sans_reservation(self):
        """Test de retrait d'un véhicule sans réservation"""
        self.parc.ajouter_vehicule(self.voiture1)
        resultat = self.parc.retirer_vehicule(self.voiture1.id)

        self.assertTrue(resultat)
        self.assertNotIn(self.voiture1, self.parc.vehicules)

    def test_retrait_vehicule_avec_reservation_active(self):
        """Test de retrait d'un véhicule avec réservation active (doit échouer)"""
        self.parc.ajouter_vehicule(self.voiture1)

        # Ajout d'une réservation future
        reservation = Reservation(
            id=1, client_id=101, vehicule_id=self.voiture1.id,
            date_debut=self.demain, date_fin=self.dans_5_jours,
            statut="confirmée"
        )
        self.parc.reservations.append(reservation)

        resultat = self.parc.retirer_vehicule(self.voiture1.id)
        self.assertFalse(resultat)  # Ne doit pas pouvoir retirer

    def test_verification_disponibilite_simple(self):
        """Test de vérification de disponibilité sans conflit"""
        self.parc.ajouter_vehicule(self.voiture1)

        vehicules_dispo = self.parc.verifier_disponibilite(
            "Voiture", {}, self.demain, self.dans_5_jours
        )

        self.assertEqual(len(vehicules_dispo), 1)
        self.assertEqual(vehicules_dispo[0].id, self.voiture1.id)

    def test_verification_disponibilite_avec_conflit(self):
        """Test de vérification de disponibilité avec conflit"""
        self.parc.ajouter_vehicule(self.voiture1)

        # Ajout d'une réservation qui bloque
        reservation = Reservation(
            id=1, client_id=101, vehicule_id=self.voiture1.id,
            date_debut=self.demain, date_fin=self.dans_5_jours,
            statut="confirmée"
        )
        self.parc.reservations.append(reservation)

        # Même période : doit être indisponible
        vehicules_dispo = self.parc.verifier_disponibilite(
            "Voiture", {}, self.demain, self.dans_5_jours
        )

        self.assertEqual(len(vehicules_dispo), 0)

    def test_verification_disponibilite_criteres_puissance(self):
        """Test de vérification avec critères de puissance"""
        self.parc.ajouter_vehicule(self.voiture1)  # 90 cv
        self.parc.ajouter_vehicule(self.voiture2)  # 130 cv

        # Recherche véhicules > 100 cv
        criteres = {"puissance": {"min": 100}}
        vehicules_dispo = self.parc.verifier_disponibilite(
            "Voiture", criteres, self.demain, self.dans_5_jours
        )

        self.assertEqual(len(vehicules_dispo), 1)
        self.assertEqual(vehicules_dispo[0].id, self.voiture2.id)  # Seule la 308

    def test_verification_disponibilite_criteres_carburant(self):
        """Test de vérification avec critères de carburant"""
        self.parc.ajouter_vehicule(self.voiture1)  # Essence
        self.parc.ajouter_vehicule(self.voiture2)  # Diesel

        criteres = {"carburant": "Diesel"}
        vehicules_dispo = self.parc.verifier_disponibilite(
            "Voiture", criteres, self.demain, self.dans_5_jours
        )

        self.assertEqual(len(vehicules_dispo), 1)
        self.assertEqual(vehicules_dispo[0].carburant, "Diesel")

    def test_enregistrement_reservation_valide(self):
        """Test d'enregistrement d'une réservation valide"""
        self.parc.ajouter_vehicule(self.voiture1)

        reservation = Reservation(
            id=1, client_id=101, vehicule_id=self.voiture1.id,
            date_debut=self.demain, date_fin=self.dans_5_jours
        )

        resultat = self.parc.enregistrer_reservation(reservation)
        self.assertTrue(resultat)
        self.assertIn(reservation, self.parc.reservations)

    def test_enregistrement_reservation_vehicule_inexistant(self):
        """Test d'enregistrement pour un véhicule inexistant (doit échouer)"""
        reservation = Reservation(
            id=1, client_id=101, vehicule_id=999,  # Véhicule inexistant
            date_debut=self.demain, date_fin=self.dans_5_jours
        )

        resultat = self.parc.enregistrer_reservation(reservation)
        self.assertFalse(resultat)

    def test_trouver_vehicule_par_id(self):
        """Test de recherche d'un véhicule par ID"""
        self.parc.ajouter_vehicule(self.voiture1)

        vehicule_trouve = self.parc._trouver_vehicule_par_id(self.voiture1.id)
        self.assertEqual(vehicule_trouve, self.voiture1)

        vehicule_inexistant = self.parc._trouver_vehicule_par_id(999)
        self.assertIsNone(vehicule_inexistant)


if __name__ == '__main__':
    unittest.main()