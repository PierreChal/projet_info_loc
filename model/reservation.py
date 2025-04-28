# Contient la logique métier (gestion_reservation.py, gestion_facturation.py…).
from datetime import datetime

class Reservation:
    """Classe représentant une réservation de véhicule par un client."""

    _compteur_id = 1  # ID auto-généré

    def __init__(self, client, vehicule, date_debut, date_fin):
        self._id_reservation = Reservation._compteur_id
        Reservation._compteur_id += 1

        self.client = client  # Client associé
        self.vehicule = vehicule  # Véhicule réservé
        self.date_debut = date_debut
        self.date_fin = date_fin
        self._statut = "En cours"

    @property
    def id_reservation(self):
        return self._id_reservation

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def vehicule(self):
        return self._vehicule

    @vehicule.setter
    def vehicule(self, value):
        self._vehicule = value

    @property
    def date_debut(self):
        return self._date_debut

    @date_debut.setter
    def date_debut(self, value):
        self._date_debut = value

    @property
    def date_fin(self):
        return self._date_fin

    @date_fin.setter
    def date_fin(self, value):
        self._date_fin = value

    @property
    def prix_total(self):
        return self._prix_total

    @property
    def statut(self):
        return self._statut

    def calculer_prix(self):
        """Calcule le prix total de la réservation."""
        nb_jours = (self.date_fin - self.date_debut).days + 1
        return round(nb_jours * self.vehicule.prix_journalier, 2)

    def annuler_reservation(self):
        """Annule la réservation."""
        self._statut = "Annulée"
        self.vehicule.changer_disponibilite(True)

    def modifier_dates(self, nouvelle_date_debut, nouvelle_date_fin):
        """Modifie les dates d'une réservation et recalcule le prix."""
        self.date_debut = nouvelle_date_debut
        self.date_fin = nouvelle_date_fin
        self._prix_total = self.calculer_prix()


# Test rapide
if __name__ == "__main__":
    from models.client import Client
    from models.vehicule import Vehicule

    # client = Client("Durand", "Alice", "alice.durand@email.com", "0623456789")
    # vehicule = Vehicule("Peugeot", "208", 2022, 45.0, True, 10000)
    #
    # debut = datetime(2025, 4, 1)
    # fin = datetime(2025, 4, 5)
    #
    # reservation = Reservation(client, vehicule, debut, fin)
    #
    # print(f"Réservation #{reservation.id_reservation} pour {reservation.client.nom} :")
    # print(f" - Véhicule : {reservation.vehicule.marque} {reservation.vehicule.modele}")
    # print(f" - Du {reservation.date_debut.date()} au {reservation.date_fin.date()}")
    # print(f" - Prix total : {reservation.prix_total}€")
    # print(f" - Statut : {reservation.statut}")