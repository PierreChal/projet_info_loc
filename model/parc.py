# model/parc.py
# ce fichier implémente la classe Parc pour gérer l'ensemble des véhicules disponibles
# il fait partie de l'architecture MVC (modèle-vue-contrôleur)
#
# structure:
# - définit la classe Parc qui gère une collection de véhicules et leurs réservations
# - implémente des algorithmes de vérification de disponibilité avec récursivité
# - fournit des méthodes pour filtrer les véhicules selon différents critères
# - propose des fonctionnalités d'optimisation et d'analyse du parc
#
# interactions:
# - utilisé par le ParcController pour gérer l'inventaire des véhicules
# - dépend des classes Véhicule et Réservation pour ses opérations
# - fournit des méthodes d'analyse pour aider à la prise de décision
# - sert de modèle central pour toute la gestion de la flotte de véhicules

from datetime import datetime, timedelta
from model.vehicule import Vehicule, Voiture, Utilitaire, Moto


class Parc:
    """
    le parc de véhicules dispo à la loc.
    gère l'ensemble des véhicules et leur dispo

    Attributes:
        vehicules (list): Liste des véhicules du parc
        reservations (list): Liste des réservations associées au parc
    """

    def __init__(self):
        """
        initialise d'un nouveau parc
        """
        # init des listes
        self.vehicules = []
        self.reservations = []

    def ajouter_vehicule(self, vehicule):
        """
        ajoute un véhicule au parc.

        Args:
            vehicule (Vehicule): Véhicule à ajouter

        Returns:
            bool: True si l'ajout a réussi
        """
        # vérifie que le véhicule n'est pas déjà dans le parc
        if vehicule not in self.vehicules:
            self.vehicules.append(vehicule)
            return True
        return False

    def retirer_vehicule(self, vehicule_id):
        """
        retire un véhicule du parc.

        Args:
            vehicule_id (int): ID du véhicule à retirer

        Returns:
            bool: True si le retrait a réussi, False sinon
        """
        # recherche du véhicule par son ID
        for i, vehicule in enumerate(self.vehicules):
            if vehicule.id == vehicule_id:
                # vérification qu'il n'y a pas de réservation active
                if self._a_reservations_actives(vehicule_id):
                    return False  # ne peut pas retirer un véhicule avec des réservations actives

                # retrait du véhicule
                self.vehicules.pop(i)
                return True

        # pas de véhicule trouvé
        return False

    def _a_reservations_actives(self, vehicule_id):
        """
        vérif si véhicule a des réservations actives

        Args:
            vehicule_id (int): ID du véhicule à vérifier

        Returns:
            bool: True si le véhicule a des réservations actives, False sinon
        """
        aujourd_hui = datetime.now()

        for reservation in self.reservations:
            # vérif que c'est bien le véhicule concerné et la date de fin est dans le futur
            if (reservation.vehicule_id == vehicule_id and
                    reservation.statut == "confirmée" and
                    reservation.date_fin >= aujourd_hui):
                return True
        return False

    def enregistrer_reservation(self, reservation):
        """
        Enregistrement dans le parc

        Args:
            reservation: Objet Reservation à enregistrer

        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        # vérif de l'existance dans le parc
        vehicule_trouve = False
        for vehicule in self.vehicules:
            if vehicule.id == reservation.vehicule_id:
                vehicule_trouve = True
                break

        if not vehicule_trouve:
            return False  # véhicule non trouvé

        # pas de conflit avec autre résa
        for autre_reservation in self.reservations:
            if reservation.est_en_conflit_avec(autre_reservation):
                return False  # conflit détecté

        # enregistrement
        self.reservations.append(reservation)
        return True

    def verifier_disponibilite(self, type_vehicule, criteres, date_debut, date_fin):
        """
        vérif la dispo des véhicules correspondant aux critères sur la période
        utilisation de recusrivité pour les périodes

        Args:
            type_vehicule (str): Type de véhicule recherché ('Voiture', 'Utilitaire', 'Moto')
            criteres (dict): Critères spécifiques de recherche
            date_debut (datetime): Date de début de la période
            date_fin (datetime): Date de fin de la période

        Returns:
            list: Liste des véhicules disponibles correspondant aux critères
        """

        # on fait une fonction récursive interne pour la dispo
        def verifier_periode_recursive(vehicule, date_debut, date_fin):
            """
            récursivité pour savoir si véhicule dispo pour dates donnés et donne les dates qu'il reste

            Args:
                vehicule (Vehicule): Véhicule à vérifier
                date_debut (datetime): Date de début de la période
                date_fin (datetime): Date de fin de la période

            Returns:
                bool: True si le véhicule est disponible, False sinon
            """
            # si la période est invalide
            if date_debut > date_fin:
                return True

            # Recherche un conflit avec une résa déjà passée
            for reservation in self.reservations:
                # réservations pour ce véhicule et qui sont "confirmées"
                if (reservation.vehicule_id == vehicule.id and
                        reservation.statut == "confirmée"):

                    # Cas 1: La résa est entièrement avant
                    if reservation.date_fin < date_debut:
                        continue  # pas de prb

                    # Cas 2: La résa est entièrement après
                    if reservation.date_debut > date_fin:
                        continue  # pas de prb

                    # Cas 3: résa chevauche le début de la période
                    if reservation.date_debut <= date_debut and reservation.date_fin < date_fin:
                        # on vérifie récursivement la partie restante de la période
                        return verifier_periode_recursive(vehicule, reservation.date_fin + timedelta(days=1), date_fin)

                    # Cas 4: idem pour la fin
                    if reservation.date_debut > date_debut and reservation.date_fin >= date_fin:
                        # idem
                        return verifier_periode_recursive(vehicule, date_debut, reservation.date_debut - timedelta(days=1))

                    # Cas 5: La résa englobe complètement la période
                    if reservation.date_debut <= date_debut and reservation.date_fin >= date_fin:
                        return False  # gros prb

                    # Cas 6: la résa est incluse dans la période donnée
                    if reservation.date_debut > date_debut and reservation.date_fin < date_fin:
                        # on doit vérifier les parties de la période restante
                        return (verifier_periode_recursive(vehicule, date_debut, reservation.date_debut - timedelta(days=1)) and
                                verifier_periode_recursive(vehicule, reservation.date_fin + timedelta(days=1), date_fin))

            # Si on arrive ici, pas de prb (c'est super)
            return True

        # recherche du type demandé
        vehicules_du_type = []
        for vehicule in self.vehicules:
            # utilisation de isinstance(objet, classe) qui vérifie si "objet" est une instance directe ou héritée de la "classe"
            if type_vehicule == 'Voiture' and isinstance(vehicule, Voiture):
                vehicules_du_type.append(vehicule)
            elif type_vehicule == 'Utilitaire' and isinstance(vehicule, Utilitaire):
                vehicules_du_type.append(vehicule)
            elif type_vehicule == 'Moto' and isinstance(vehicule, Moto):
                vehicules_du_type.append(vehicule)

        # selon les critères
        vehicules_filtres = []
        for vehicule in vehicules_du_type:
            if self._correspond_criteres(vehicule, criteres):
                vehicules_filtres.append(vehicule)

        # vérif de dispo pour chaque véhicule filtré
        vehicules_disponibles = []
        for vehicule in vehicules_filtres:
            if verifier_periode_recursive(vehicule, date_debut, date_fin):
                vehicules_disponibles.append(vehicule) # on utilise la récursivité ici pour savoir si parmis les véhicules conserver les dates sont bonnes

        return vehicules_disponibles

    def _correspond_criteres(self, vehicule, criteres):
        """
        vérif un véhicule correspond aux critères

        Args:
            vehicule (Vehicule): Véhicule à vérifier
            criteres (dict): Critères de recherche (e.g. {"places": 5, "marque": "Renault"} )

        Returns:
            bool: True si le véhicule correspond aux critères, False sinon
        """
        # cas sans rien
        if not criteres:
            return True

        # vérif des critères
        for cle, valeur in criteres.items():
            # cas sans clé
            if not hasattr(vehicule, cle):
                return False

            # récupère la valeur de l'attribut
            attr_valeur = getattr(vehicule, cle)

            # comparaison selon le type
            if isinstance(valeur, dict):
                # Critère  min/max
                if "min" in valeur and attr_valeur < valeur["min"]:
                    return False
                if "max" in valeur and attr_valeur > valeur["max"]:
                    return False
            elif isinstance(attr_valeur, list) and isinstance(valeur, str):
                # Recherche dans une liste (ex: options)
                if valeur not in attr_valeur:
                    return False
            elif attr_valeur != valeur:
                # Comparaison simple
                return False

        # tous les critères sont satisfaits (génial !)
        return True

    def optimiser_parc(self, historique_reservations, budget_annuel=None):
        """
        Optimise le parc de véhicules en fonction de l'historique des réservations.
        Utilise un algorithme d'optimisation pour maximiser le taux d'utilisation
        tout en respectant les contraintes budgétaires.

        Args:
            historique_reservations (list): Historique complet des réservations passées
            budget_annuel (float, optional): Budget disponible pour l'acquisition de nouveaux véhicules

        Returns:
            dict: Recommandations pour l'optimisation du parc
        """
        # TODO: faire cette fonciton
        return

    def _calculer_taux_utilisation(self, historique_reservations):
        """
        Calcule le taux d'utilisation de chaque véhicule sur l'année écoulée.

        Args:
            historique_reservations (list): Historique des réservations

        Returns:
            dict: Dictionnaire {vehicule_id: taux_utilisation}
        """
        # Date de début de l'analyse (1 an en arrière)
        date_debut_analyse = datetime.now() - timedelta(days=365)

        # Jours totaux dans la période (1 an = 365 jours)
        jours_total = 365

        # Initialisation du compteur de jours réservés pour chaque véhicule
        jours_reserves = {vehicule.id: 0 for vehicule in self.vehicules}

        # Comptage des jours réservés pour chaque véhicule
        for reservation in historique_reservations:
            # On ne considère que les réservations terminées ou confirmées
            if reservation.statut in ["terminée", "confirmée"]:
                vehicule_id = reservation.vehicule_id

                # On ne compte que si le véhicule est toujours dans notre parc
                if vehicule_id in jours_reserves:
                    # Date de début à considérer (max entre début réservation et début analyse)
                    date_debut_effective = max(reservation.date_debut, date_debut_analyse)

                    # Date de fin à considérer (aujourd'hui si la réservation est en cours)
                    date_fin_effective = min(reservation.date_fin, datetime.now())

                    # Calcul du nombre de jours
                    if date_fin_effective >= date_debut_effective:  # Vérification de validité
                        duree = (date_fin_effective - date_debut_effective).days + 1
                        jours_reserves[vehicule_id] += duree

        # Calcul du taux d'utilisation (jours réservés / jours totaux)
        taux_utilisation = {}
        for vehicule_id, jours in jours_reserves.items():
            # Le taux est plafonné à 100%
            taux_utilisation[vehicule_id] = min(jours / jours_total, 1.0)

        return taux_utilisation

    def _analyser_demandes_refusees(self, historique_reservations):
        """
        Analyse les demandes qui n'ont pas pu être satisfaites.
        Note: Ceci est une version simplifiée. Dans une implémentation complète,
        on utiliserait un historique des demandes refusées.

        Args:
            historique_reservations (list): Historique des réservations

        Returns:
            dict: Statistiques sur les demandes refusées
        """
        # Version simplifiée : on suppose que toutes les réservations annulées
        # sont dues à des problèmes de disponibilité (ce qui est une approximation)
        demandes_refusees = {
            "Voiture": 0,
            "Utilitaire": 0,
            "Moto": 0
        }

        # Comptage des réservations annulées par type de véhicule
        for reservation in historique_reservations:
            if reservation.statut == "annulée":
                # Recherche du type de véhicule
                for vehicule in self.vehicules:
                    if vehicule.id == reservation.vehicule_id:
                        type_vehicule = vehicule.__class__.__name__
                        demandes_refusees[type_vehicule] += 1
                        break

        return demandes_refusees

    def _trouver_vehicule_par_id(self, vehicule_id):
        """
        Trouve un véhicule par son ID dans la liste des véhicules du parc

        Args:
            vehicule_id (int): ID du véhicule à rechercher

        Returns:
            Vehicule: Le véhicule trouvé ou None si non trouvé
        """
        for vehicule in self.vehicules:
            if vehicule.id == vehicule_id:
                return vehicule
        return None

    def obtenir_vehicule(self, vehicule_id):
        """
        Alias public pour _trouver_vehicule_par_id

        Args:
            vehicule_id (int): ID du véhicule

        Returns:
            Vehicule: Le véhicule trouvé ou None
        """
        return self._trouver_vehicule_par_id(vehicule_id)

    def ajouter_vehicule(self, vehicule):
        """
        Ajoute un véhicule au parc

        Args:
            vehicule: Instance du véhicule à ajouter
        """
        if vehicule and vehicule not in self.vehicules:
            self.vehicules.append(vehicule)
            return True
        return False

    def retirer_vehicule(self, vehicule_id):
        """
        Retire un véhicule du parc par son ID

        Args:
            vehicule_id (int): ID du véhicule à retirer

        Returns:
            bool: True si retiré avec succès, False sinon
        """
        vehicule = self._trouver_vehicule_par_id(vehicule_id)
        if vehicule:
            self.vehicules.remove(vehicule)
            return True
        return False


# exemple de ce fichier (n'est executé que si l'on RUN ce fichier)
if __name__ == "__main__":
    from datetime import datetime, timedelta
    from model.vehicule import Voiture, Utilitaire, Moto
    from model.reservation import Reservation

    parc = Parc()

    # quelques véhicules
    voiture1 = Voiture(
        id=1,
        marque="Renault",
        modele="Clio",
        annee=2020,
        kilometrage=15000,
        prix_achat=15000,
        cout_entretien_annuel=1000,
        nb_places=5,
        puissance=90,
        carburant="Essence",
        options=["Climatisation", "GPS"]
    )

    voiture2 = Voiture(
        id=2,
        marque="Peugeot",
        modele="308",
        annee=2019,
        kilometrage=25000,
        prix_achat=18000,
        cout_entretien_annuel=1200,
        nb_places=5,
        puissance=120,
        carburant="Diesel",
        options=["Climatisation", "GPS", "Sièges chauffants"]
    )

    utilitaire = Utilitaire(
        id=3,
        marque="Renault",
        modele="Master",
        annee=2018,
        kilometrage=40000,
        prix_achat=25000,
        cout_entretien_annuel=1500,
        volume=12,
        charge_utile=1200,
        hayon=True
    )

    # ajout des véhicules au parc
    parc.ajouter_vehicule(voiture1)
    parc.ajouter_vehicule(voiture2)
    parc.ajouter_vehicule(utilitaire)

    # création de quelques réservations
    aujourd_hui = datetime.now()

    reservation1 = Reservation(
        id=1,
        client_id=101,
        vehicule_id=1,
        date_debut=aujourd_hui + timedelta(days=5),
        date_fin=aujourd_hui + timedelta(days=10),
        prix_total=300,
        statut="confirmée"
    )

    reservation2 = Reservation(
        id=2,
        client_id=102,
        vehicule_id=2,
        date_debut=aujourd_hui + timedelta(days=7),
        date_fin=aujourd_hui + timedelta(days=12),
        prix_total=350,
        statut="confirmée"
    )

    # enregistrement
    parc.enregistrer_reservation(reservation1)
    parc.enregistrer_reservation(reservation2)

    # test de vérification de dispo
    date_test_debut = aujourd_hui + timedelta(days=15)
    date_test_fin = aujourd_hui + timedelta(days=20)

    print("Véhicules disponibles:")
    vehicules_dispo = parc.verifier_disponibilite("Voiture", {"carburant": "Essence"}, date_test_debut, date_test_fin)
    for vehicule in vehicules_dispo:
        print(f"- {vehicule}")

    # création d'un historique de réservations pour le test d'optimisation (TODO)
    historique = []

    # Réservations passées pour voiture1 (beaucoup de réservations = forte demande)
    for i in range(30):
        debut = aujourd_hui - timedelta(days=365 - i * 10)
        fin = debut + timedelta(days=8)
        historique.append(Reservation(
            id=100 + i,
            client_id=101,
            vehicule_id=1,
            date_debut=debut,
            date_fin=fin,
            prix_total=300,
            statut="terminée"
        ))

    # Réservations passées pour voiture2 (peu de réservations = sous-utilisation)
    for i in range(3):
        debut = aujourd_hui - timedelta(days=300 - i * 30)
        fin = debut + timedelta(days=5)
        historique.append(Reservation(
            id=200 + i,
            client_id=102,
            vehicule_id=2,
            date_debut=debut,
            date_fin=fin,
            prix_total=350,
            statut="terminée"
        ))

