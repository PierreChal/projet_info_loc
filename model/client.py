# model/client.py
# ici, on fait les classes pour la gestion des clients

class Client:
    """
    classe représentant un client de location avec toutes les données qui y sont lieés

    Attributes:
        id (int): Identifiant unique du client
        nom (str): Nom de famille du client
        prenom (str): Prénom du client
        adresse (str): Adresse postale complète
        telephone (str): Numéro de téléphone
        email (str): Adresse email
        historique_reservations (list): Liste des réservations passées (optionnel)
    """

    def __init__(self, id, nom, prenom, adresse, telephone, email, historique_reservations=None):
        """
        initialisation du client
        """
        # Informations de bases
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.adresse = adresse
        self.telephone = telephone
        self.email = email

        # historique des réservations (lsite vide si rien)
        if historique_reservations is None:
            self.historique_reservations = []
        else:
            self.historique_reservations = historique_reservations

    def ajouter_reservation(self, reservation):
        """
        ajoute de réservation à l'historique

        Args:
            reservation: Objet Reservation à ajouter à l'historique
        """
        # on check si ce n'est pas déjà pris en compte et on l'ajoute
        if reservation not in self.historique_reservations:
            self.historique_reservations.append(reservation)

    def obtenir_reservations_en_cours(self):
        """
        permet ici de récupérer toutes les réservations en cours (non terminées et non annulées)

        Returns:
            list: Liste des réservations en cours
        """
        # on fait une liste avec seulement les réservation dites "confirmée"
        return [reservation for reservation in self.historique_reservations
                if reservation.statut == "confirmée"]

    def obtenir_reservations_passees(self):
        """
        idem pour les reservation terminée

        Returns:
            list: Liste des réservations passées
        """
        return [reservation for reservation in self.historique_reservations
                if reservation.statut == "terminée"]

    def calculer_montant_total_depense(self):
        """
        pour les reservations terminées on ajoute les dépenses totales

        Returns:
            float: Montant total en euros
        """
        # On additionne le prix de toutes les réservations terminées
        reservations_terminees = self.obtenir_reservations_passees()
        total = sum(reservation.prix_total for reservation in reservations_terminees)
        # .pris_total est un attribut présent dans la classe reservation
        return total

    def est_client_fidele(self, seuil_reservations=5):
        """
        permet de voir un client fidèle selon un seuil que l'ont choisi

        Args:
            seuil_reservations (int): Nombre minimum de réservations pour être considéré fidèle

        Returns:
            bool: True si le client est fidèle, False sinon
        """
        # on compte toutes les réservations passées ou terminées
        nb_reservations_total = len(self.obtenir_reservations_passees()) + len(self.obtenir_reservations_en_cours())
        return nb_reservations_total >= seuil_reservations

    def mettre_a_jour_coordonnees(self, adresse=None, telephone=None, email=None):
        """
        met à jour des coordonnées

        Args:
            adresse (str, optional): Nouvelle adresse
            telephone (str, optional): Nouveau numéro de téléphone
            email (str, optional): Nouvelle adresse email
        """
        # on met à jour les champs fourni dans la fonction (pour éviter de faire 3 fonctions différentes)
        if adresse is not None:
            self.adresse = adresse
        if telephone is not None:
            self.telephone = telephone
        if email is not None:
            self.email = email

    def __str__(self):
        """
        mise en page des attributs
        """
        return f"{self.prenom} {self.nom} - {self.email} - {self.telephone}"


# exemple de ce fichier (n'est executé que si l'on RUN ce fichier)
if __name__ == "__main__":
    from datetime import datetime, timedelta

    client = Client(
        id=1,
        nom="Michael",
        prenom="Schumacher",
        adresse="1 rue de la victoire, 75001 Paris",
        telephone="06 56 39 44 20",
        email="michael.schumacher@example.com"
    )

    print(client)


    # Création d'une classe Reservation juste pour l'exemple (le fromat final est défini dans reservation.py)
    class ReservationSimple:
        def __init__(self, id, vehicule_id, date_debut, date_fin, prix_total, statut="confirmée"):
            self.id = id
            self.vehicule_id = vehicule_id
            self.date_debut = date_debut
            self.date_fin = date_fin
            self.prix_total = prix_total
            self.statut = statut


    # Création de quelques réservations d'exemple
    aujourd_hui = datetime.now()
    reservation1 = ReservationSimple(
        id=101,
        vehicule_id=1,
        date_debut=aujourd_hui - timedelta(days=30),
        date_fin=aujourd_hui - timedelta(days=25),
        prix_total=250,
        statut="terminée"
    )

    reservation2 = ReservationSimple(
        id=102,
        vehicule_id=2,
        date_debut=aujourd_hui + timedelta(days=5),
        date_fin=aujourd_hui + timedelta(days=10),
        prix_total=350,
        statut="confirmée"
    )

    # ajout des réservations à l'historique du client
    client.ajouter_reservation(reservation1)
    client.ajouter_reservation(reservation2)

    print(f"Réservations en cours: {len(client.obtenir_reservations_en_cours())}")
    print(f"Réservations passées: {len(client.obtenir_reservations_passees())}")

    print(f"Montant total dépensé: {client.calculer_montant_total_depense()} €")

    print(f"Client fidèle: {client.est_client_fidele(seuil_reservations=2)}")