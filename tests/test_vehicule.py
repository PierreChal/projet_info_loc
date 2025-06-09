# tests/test_vehicule.py
# Tests unitaires pour les classes de véhicules
# Vérifie les calculs de tarifs, coûts de possession et méthodes spécifiques

import unittest
import sys
import os

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.vehicule import Voiture, Utilitaire, Moto


class TestVehicule(unittest.TestCase):

    def setUp(self):
        """Préparation des objets de test"""
        # Création d'une voiture de test
        self.voiture = Voiture(
            id=1,
            marque="Renault",
            modele="Clio",
            annee=2020,
            kilometrage=15000,
            prix_achat=15000,
            cout_entretien_annuel=600,
            nb_places=5,
            puissance=90,
            carburant="Essence",
            options=["Climatisation", "GPS"]
        )

        # Création d'un utilitaire de test
        self.utilitaire = Utilitaire(
            id=2,
            marque="Citroën",
            modele="Jumpy",
            annee=2019,
            kilometrage=30000,
            prix_achat=20000,
            cout_entretien_annuel=800,
            volume=8,
            charge_utile=1000,
            hayon=True
        )

        # Création d'une moto de test
        self.moto = Moto(
            id=3,
            marque="Honda",
            modele="CB500F",
            annee=2021,
            kilometrage=5000,
            prix_achat=7000,
            cout_entretien_annuel=400,
            cylindree=500,
            type_moto="Roadster"
        )

    def test_calcul_tarif_voiture(self):
        """Test du calcul de tarif journalier pour une voiture"""
        # Voiture avec puissance 90 cv + 2 options
        tarif = self.voiture.calculer_tarif_journalier()
        expected = 40 + (2 * 5)  # 40€ base + 10€ options
        self.assertEqual(tarif, expected)

    def test_calcul_tarif_utilitaire(self):
        """Test du calcul de tarif journalier pour un utilitaire"""
        # Utilitaire 8m³ avec hayon
        tarif = self.utilitaire.calculer_tarif_journalier()
        expected = 70 + 10  # 70€ base + 10€ hayon
        self.assertEqual(tarif, expected)

    def test_calcul_tarif_moto(self):
        """Test du calcul de tarif journalier pour une moto"""
        # Moto 500cc
        tarif = self.moto.calculer_tarif_journalier()
        expected = 40  # 500cc = tarif moyen
        self.assertEqual(tarif, expected)

    def test_cout_possession_5_ans(self):
        """Test du calcul de coût de possession sur 5 ans"""
        cout = self.voiture.calculer_cout_possession(5)
        expected = (15000 / 5 + 600) * 5  # amortissement + entretien
        self.assertEqual(cout, expected)

    def test_cout_possession_plus_5_ans(self):
        """Test du calcul de coût de possession au-delà de 5 ans"""
        cout = self.voiture.calculer_cout_possession(7)
        # 5 premières années + 2 années entretien seulement
        expected = (15000 / 5 + 600) * 5 + 600 * 2
        self.assertEqual(cout, expected)

    def test_ajout_option_voiture(self):
        """Test de l'ajout d'options à une voiture"""
        initial_options = len(self.voiture.options)
        self.voiture.ajouter_option("Bluetooth")
        self.assertEqual(len(self.voiture.options), initial_options + 1)
        self.assertIn("Bluetooth", self.voiture.options)

    def test_representation_string(self):
        """Test de la représentation textuelle des véhicules"""
        voiture_str = str(self.voiture)
        self.assertIn("Renault", voiture_str)
        self.assertIn("Clio", voiture_str)
        self.assertIn("2020", voiture_str)


if __name__ == '__main__':
    unittest.main()