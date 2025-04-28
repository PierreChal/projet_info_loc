from datetime import datetime

class Facture:
    """Classe représentant une facture associée à une réservation."""

    _compteur_id = 1

    def __init__(self, reservation):
        self._id_facture = Facture._compteur_id
        Facture._compteur_id += 1

        self.reservation = reservation
        self._montant_total = reservation.prix_total
        self._date_facture = datetime.now()
        self._etat_paiement = "Non Payée"

    @property
    def id_facture(self):
        return self._id_facture

    @property
    def montant_total(self):
        return self._montant_total

    @property
    def date_facture(self):
        return self._date_facture

    @property
    def etat_paiement(self):
        return self._etat_paiement

    def marquer_comme_payee(self):
        """Met à jour le statut de la facture."""
        self._etat_paiement = "Payée"

    def generer_facture(self):
        """Génère une facture texte simulée (à remplacer par PDF plus tard)."""
        print("\n📄 FACTURE")
        print(f"ID Facture : {self.id_facture}")
        print(f"Date : {self.date_facture.strftime('%Y-%m-%d')}")
        print(f"Client : {self.reservation.client.prenom} {self.reservation.client.nom}")
        print(f"Véhicule : {self.reservation.vehicule.marque} {self.reservation.vehicule.modele}")
        print(f"Du {self.reservation.date_debut.date()} au {self.reservation.date_fin.date()}")
        print(f"Montant : {self.montant_total:.2f} €")
        print(f"Statut : {self.etat_paiement}")


# Test rapide
if __name__ == "__main__":
    from models.client import Client
    from models.vehicule import Vehicule
    from models.reservation import Reservation

    client = Client("Durand", "Alice", "alice.durand@email.com", "0623456789")
    vehicule = Vehicule("Peugeot", "208", 2022, 45.0, True, 10000)
    reservation = Reservation(client, vehicule, datetime(2025, 4, 1), datetime(2025, 4, 5))

    facture = Facture(reservation)
    facture.generer_facture()

    facture.marquer_comme_payee()
    print("\n✅ Paiement enregistré !")
    facture.generer_facture()