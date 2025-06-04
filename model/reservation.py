# model/reservation.py
# ce fichier définit la classe Reservation pour gérer les locations de véhicules
# il fait partie de l'architecture MVC (modèle-vue-contrôleur)
#
# structure:
# - implémente la classe Reservation avec ses attributs et méthodes
# - définit le cycle de vie d'une réservation (confirmée, annulée, terminée)
# - intègre le pattern Observer pour notifier des changements de statut
# - calcule les prix en fonction de la durée et du type de véhicule
#
# interactions:
# - utilisé par le ReservationController pour gérer le cycle de vie des réservations
# - lie un client à un véhicule spécifique pour une période donnée
# - communique avec les classes Client et Véhicule
# - permet la vérification des conflits de réservation
# - notifie les observateurs des changements importants de statut

from datetime import datetime, timedelta


class Reservation:
    """
    classe représentant une réservation de véhicule (c.f. classe du même nom)

    Attributes:
        id (int): Identifiant unique de la réservation
        client_id (int): ID du client qui effectue la réservation
        vehicule_id (int): ID du véhicule réservé
        date_debut (datetime): Date et heure de début de la réservation
        date_fin (datetime): Date et heure de fin de la réservation
        prix_total (float): Prix total de la réservation
        statut (str): Statut de la réservation ('confirmée', 'annulée', 'terminée')
    """

    # statuts possibles
    STATUT_CONFIRMEE = "confirmée"
    STATUT_ANNULEE = "annulée"
    STATUT_TERMINEE = "terminée"

    def __init__(self, id, client_id, vehicule_id, date_debut, date_fin, prix_total=None, statut=None):
        """
        Initialisation

        Args:
            id (int): Identifiant unique de la réservation
            client_id (int): ID du client qui effectue la réservation
            vehicule_id (int): ID du véhicule réservé
            date_debut (datetime): Date et heure de début de la réservation
            date_fin (datetime): Date et heure de fin de la réservation
            prix_total (float, optional): Prix total de la réservation (calculé automatiquement si None)
            statut (str, optional): Statut initial de la réservation (confirmée par défaut)
        """
        # vérif date est bonne
        if date_fin <= date_debut:
            raise ValueError("Attention ! La date de fin doit être postérieure à la date de début")

        # attributs de base
        self.id = id
        self.client_id = client_id
        self.vehicule_id = vehicule_id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.prix_total = prix_total

        # Statut par défaut est "confirmée" et évolue vers les autres
        if statut is None:
            self.statut = self.STATUT_CONFIRMEE
        else:
            # vérif status dans les 3 choix possible
            if statut not in [self.STATUT_CONFIRMEE, self.STATUT_ANNULEE, self.STATUT_TERMINEE]:
                raise ValueError(f"Statut invalide: {statut}")
            self.statut = statut

        # liste pour stocker les observateurs (pattern Observer) pour notifier des changements d'états de reservations
        self._observateurs = []

    def calculer_prix(self, vehicule):
        """
        FONCTION MODIFIÉE - Calcule le prix en fonction de la DURÉE et du véhicule

        CHANGEMENTS:
        - Ajout du calcul de durée en jours
        - Multiplication tarif × nombre de jours
        - Application de réductions selon la durée
        - Mise à jour automatique de self.prix_total

        Args:
            vehicule: Instance du véhicule réservé

        Returns:
            float: Prix total calculé
        """
        # NOUVEAU: Calcul de la durée réelle
        nb_jours = self.calculer_duree_jours()

        # NOUVEAU: Récupération du tarif journalier du véhicule
        tarif_journalier = vehicule.calculer_tarif_journalier()

        # NOUVEAU: Calcul du prix de base (tarif × durée)
        prix_base = tarif_journalier * nb_jours

        # NOUVEAU: Application des réductions pour longue durée
        if nb_jours >= 30:  # Plus d'un mois
            prix_final = prix_base * 0.8  # 20% de réduction
        elif nb_jours >= 7:  # Plus d'une semaine
            prix_final = prix_base * 0.9  # 10% de réduction
        else:
            prix_final = prix_base  # Pas de réduction

        # NOUVEAU: Mise à jour automatique du prix total
        self.prix_total = round(prix_final, 2)

        return self.prix_total

    def obtenir_details_prix(self, vehicule):
        """
        Retourne le détail du calcul pour affichage

        Returns:
            dict: Tous les détails du calcul de prix
        """
        nb_jours = self.calculer_duree_jours()
        tarif_journalier = vehicule.calculer_tarif_journalier()
        prix_base = tarif_journalier * nb_jours

        # Calcul de la réduction
        if nb_jours >= 30:
            reduction_pourcent = 20
            prix_final = prix_base * 0.8
        elif nb_jours >= 7:
            reduction_pourcent = 10
            prix_final = prix_base * 0.9
        else:
            reduction_pourcent = 0
            prix_final = prix_base

        return {
            'nb_jours': nb_jours,
            'tarif_journalier': round(tarif_journalier, 2),
            'prix_base': round(prix_base, 2),
            'reduction_pourcent': reduction_pourcent,
            'prix_final': round(prix_final, 2),
            'economie': round(prix_base - prix_final, 2)
        }

    def annuler(self):
        """
        annule la reservation si elle est confirmée

        Returns:
            bool: True si l'annulation a réussi, False sinon
        """
        if self.statut == self.STATUT_CONFIRMEE:
            ancien_statut = self.statut
            self.statut = self.STATUT_ANNULEE

            # notification des observateurs, changement d'état
            self._notifier_observateurs("annulation", ancien_statut, self.statut) # méthode définie plus tard

            return True
        else:
            # pas possible d'annuler la résa
            return False

    def terminer(self):
        """
        résa devient terminée si elle est en statut confirmée, idem que annuler()

        Returns:
            bool: True si la terminaison a réussi, False sinon
        """
        if self.statut == self.STATUT_CONFIRMEE:
            ancien_statut = self.statut
            self.statut = self.STATUT_TERMINEE

            self._notifier_observateurs("terminaison", ancien_statut, self.statut)

            return True
        else:
            return False

    def est_active_a_date(self, date):
        """
        Vérif si la date est dans la résa

        Args:
            date (datetime): Date à vérifier

        Returns:
            bool: True si la réservation est active à cette date, False sinon
        """
        # vérification statut est une résa confirmée
        return (self.statut == self.STATUT_CONFIRMEE and
                self.date_debut <= date <= self.date_fin) # format compact de directement dans le return

    def est_en_conflit_avec(self, autre_reservation):
        """
        Deux réservations sont en conflit si elles concernent le même véhicule,

        Args:
            autre_reservation (Reservation): Autre réservation à comparer

        Returns:
            bool: True s'il y a conflit, False sinon
        """
        # on veut pas que se soit le même véhicule que celui considéré
        if self.vehicule_id != autre_reservation.vehicule_id:
            return False

        # on veut que ce soit bien des résa confirmée
        if (self.statut != self.STATUT_CONFIRMEE or
                autre_reservation.statut != self.STATUT_CONFIRMEE):
            return False

        # chevauchement des périodes à check
        # il faut que l'une se termine avant que l'autre ne commence on procède par l'absrude ici
        if (self.date_fin < autre_reservation.date_debut or
                self.date_debut > autre_reservation.date_fin):
            return False
        return True

    def duree_en_jours(self):
        """
        durée de la résa

        Returns:
            int: Nombre de jours de la réservation
        """
        # +1 car on compte le jour de début et de fin
        return (self.date_fin - self.date_debut).days + 1

    def ajouter_observateur(self, observateur):
        """
        ajoute un observateur qui sera notifié des changements de statut
        c'est le pattern Observer

        Args:
            observateur: Objet ayant une méthode 'mettre_a_jour'
        """
        if observateur not in self._observateurs:
            self._observateurs.append(observateur)

    def supprimer_observateur(self, observateur):
        """
        supprime l'observateur

        Args:
            observateur: Observateur à supprimer
        """
        if observateur in self._observateurs:
            self._observateurs.remove(observateur)

    def _notifier_observateurs(self, type_evenement, ancien_statut, nouveau_statut):
        """
        notif pour les obs d'un changement de statut

        Args:
            type_evenement (str): Type d'événement qui a eu lieu
            ancien_statut (str): Ancien statut de la réservation
            nouveau_statut (str): Nouveau statut de la réservation
        """
        for observateur in self._observateurs:
            observateur.mettre_a_jour(self, type_evenement, ancien_statut, nouveau_statut)

    def __str__(self):
        """
        représentation textuelle
        """
        # formatage des dates
        date_debut_str = self.date_debut.strftime("%d/%m/%Y")
        date_fin_str = self.date_fin.strftime("%d/%m/%Y")

        return (f"Réservation #{self.id} : "
                f"Client #{self.client_id}, Véhicule #{self.vehicule_id}, "
                f"du {date_debut_str} au {date_fin_str}, "
                f"Prix: {self.prix_total or 'Non calculé'} €, "
                f"Statut: {self.statut}")

    def calculer_duree_jours(self):
        """
        Calcule la durée en jours entre date_debut et date_fin

        Returns:
            int: Nombre de jours de la réservation (minimum 1)
        """
        duree = (self.date_fin - self.date_debut).days
        return max(1, duree)  # Au minimum 1 jour même si dates identiques

# implémentation du pattern Observer pour les notifs
class NotificationEmail:
    """
    utilisation du pattern Observer pour générer des notifs (email, mais message ou autre serait ainsi facile à mettre en palce)
    """

    def mettre_a_jour(self, reservation, type_evenement, ancien_statut, nouveau_statut):
        """
        méthode pour qu'une réservation change de statut

        Args:
            reservation (Reservation): Réservation qui a changé
            type_evenement (str): Type d'événement qui a eu lieu
            ancien_statut (str): Ancien statut de la réservation
            nouveau_statut (str): Nouveau statut de la réservation
        """
        # dans une implémentation réelle on pourrait faire en sorte d'envoyer un "vrai" mail, ou sms ou autre
        # ici c'est une Proof Of Concept qui ne fait qu'écrire une notification
        print(f"NOTIFICATION !!! : Réservation #{reservation.id} - "
              f"{type_evenement.capitalize()} - "
              f"Statut changé de '{ancien_statut}' à '{nouveau_statut}'")


# exemple de ce fichier (n'est executé que si l'on RUN ce fichier)
if __name__ == "__main__":
    from datetime import datetime, timedelta

    #création d'un résa
    aujourd_hui = datetime.now()
    debut = aujourd_hui + timedelta(days=5)  # super exemple dynamique grâcer à datetime
    fin = aujourd_hui + timedelta(days=10)

    reservation = Reservation(
        id=1,
        client_id=101,
        vehicule_id=201,
        date_debut=debut,
        date_fin=fin
    )

    print(reservation)


    # calcul de prix (pour l'exemple on fait une classe car les intercations sont une action sur les classes)
    class VehiculeTest:
        def calculer_tarif_journalier(self):
            return 50  # 50€ par jour pour l'exemple


    vehicule_test = VehiculeTest()
    prix = reservation.calculer_prix(vehicule_test)

    print(f"Prix calculé: {prix} €")
    print(reservation)  # le prix est mis à jour

    # démo pattern Observer
    notification_email = NotificationEmail()
    reservation.ajouter_observateur(notification_email)

    # annulation de la résa
    if reservation.annuler():
        print("Réservation annulée avec succès")
    else:
        print("Impossible d'annuler la réservation")

    print(reservation)  # mis à jour du statut