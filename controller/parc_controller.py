# controller/parc_controller.py
# ce fichier gère toutes les opérations liées au parc de véhicules
# il fait partie de l'architecture MVC (modèle-vue-contrôleur)
#
# structure:
# - importe les modèles parc et les types de vehicules (voiture, utilitaire, moto)
# - définit la classe parccontroller avec méthodes pour ajouter, supprimer, mettre à jour et rechercher des véhicules
# - gère la vérification de disponibilité et l'optimisation du parc
# - calcule les statistiques sur l'état du parc
#
# interactions:
# - utilise les modèles parc et vehicule pour représenter les données
# - communique avec la base de données pour persistance des informations
# - gère les opérations métier comme la vérification de disponibilité
# - fournit des interfaces pour les vues qui affichent l'état du parc

from model.parc import Parc
from model.vehicule import Voiture, Utilitaire, Moto
from datetime import datetime


class ParcController:
    """
    contrôleur pour gérer les opérations liées au parc de véhicules.
    fait le lien entre la vue et les modèles parc et vehicule.

    attributes:
        db (database): instance de la base de données
        parc (parc): instance du parc de véhicules

    author:
        [votre nom]
    """

    def __init__(self, db):
        """
        initialise le contrôleur avec une connexion à la base de données.

        args:
            db (database): instance de la base de données
        """
        self.db = db
        self.parc = Parc()
        self._charger_parc()

    def _charger_parc(self):
        """
        charge tous les véhicules et réservations depuis la base de données.
        """
        try:
            # chargement des véhicules
            vehicules = self.db.charger_tous_vehicules()
            for vehicule in vehicules:
                self.parc.ajouter_vehicule(vehicule)

            # chargement des réservations actives
            # dans une implémentation complète, il faudrait adapter cette méthode
            # selon les fonctionnalités de la base de données
            self.parc.reservations = []  # réinitialisation

            # la méthode à implémenter dans database pourrait être:
            # reservations = self.db.charger_reservations_actives()
            # for reservation in reservations:
            #     self.parc.reservations.append(reservation)

        except Exception as e:
            print(f"erreur lors du chargement du parc: {e}")

    def ajouter_vehicule(self, type_vehicule, **kwargs):
        """
        ajoute un nouveau véhicule au parc.

        args:
            type_vehicule (str): type de véhicule ('voiture', 'utilitaire', 'moto')
            **kwargs: attributs du véhicule

        returns:
            vehicule: véhicule ajouté, ou none en cas d'erreur
        """
        try:
            # validation des données communes
            attributs_communs = ['marque', 'modele', 'annee', 'kilometrage', 'prix_achat', 'cout_entretien_annuel']
            for attr in attributs_communs:
                if attr not in kwargs:
                    print(f"l'attribut {attr} est obligatoire")
                    return None

            # création du véhicule selon son type
            vehicule = None

            if type_vehicule == 'Voiture':
                # validation des attributs spécifiques
                attributs_specifiques = ['nb_places', 'puissance', 'carburant']
                for attr in attributs_specifiques:
                    if attr not in kwargs:
                        print(f"l'attribut {attr} est obligatoire pour une voiture")
                        return None

                # création de la voiture
                vehicule = Voiture(
                    id=None,
                    marque=kwargs['marque'],
                    modele=kwargs['modele'],
                    annee=kwargs['annee'],
                    kilometrage=kwargs['kilometrage'],
                    prix_achat=kwargs['prix_achat'],
                    cout_entretien_annuel=kwargs['cout_entretien_annuel'],
                    nb_places=kwargs['nb_places'],
                    puissance=kwargs['puissance'],
                    carburant=kwargs['carburant'],
                    options=kwargs.get('options', [])
                )

            elif type_vehicule == 'Utilitaire':
                # validation des attributs spécifiques
                attributs_specifiques = ['volume', 'charge_utile']
                for attr in attributs_specifiques:
                    if attr not in kwargs:
                        print(f"l'attribut {attr} est obligatoire pour un utilitaire")
                        return None

                # création de l'utilitaire
                vehicule = Utilitaire(
                    id=None,
                    marque=kwargs['marque'],
                    modele=kwargs['modele'],
                    annee=kwargs['annee'],
                    kilometrage=kwargs['kilometrage'],
                    prix_achat=kwargs['prix_achat'],
                    cout_entretien_annuel=kwargs['cout_entretien_annuel'],
                    volume=kwargs['volume'],
                    charge_utile=kwargs['charge_utile'],
                    hayon=kwargs.get('hayon', False)
                )

            elif type_vehicule == 'Moto':
                # validation des attributs spécifiques
                attributs_specifiques = ['cylindree', 'type_moto']
                for attr in attributs_specifiques:
                    if attr not in kwargs:
                        print(f"l'attribut {attr} est obligatoire pour une moto")
                        return None

                # création de la moto
                vehicule = Moto(
                    id=None,
                    marque=kwargs['marque'],
                    modele=kwargs['modele'],
                    annee=kwargs['annee'],
                    kilometrage=kwargs['kilometrage'],
                    prix_achat=kwargs['prix_achat'],
                    cout_entretien_annuel=kwargs['cout_entretien_annuel'],
                    cylindree=kwargs['cylindree'],
                    type_moto=kwargs['type_moto']
                )

            else:
                print(f"type de véhicule non reconnu: {type_vehicule}")
                return None

            # sauvegarde dans la base de données
            vehicule_id = self.db.sauvegarder_vehicule(vehicule)

            # récupération du véhicule complet
            vehicule = self.db.charger_vehicule(vehicule_id)

            # ajout au parc
            if vehicule:
                self.parc.ajouter_vehicule(vehicule)

            return vehicule

        except Exception as e:
            print(f"erreur lors de l'ajout du véhicule: {e}")
            return None

    def retirer_vehicule(self, vehicule_id):
        """
        retire un véhicule du parc.

        args:
            vehicule_id (int): id du véhicule à retirer

        returns:
            bool: true si le retrait a réussi, false sinon
        """
        try:
            # vérification que le véhicule peut être retiré
            if not self.parc.retirer_vehicule(vehicule_id):
                return False

            # suppression dans la base de données
            return self.db.supprimer_vehicule(vehicule_id)

        except Exception as e:
            print(f"erreur lors du retrait du véhicule: {e}")
            return False

    def mettre_a_jour_vehicule(self, vehicule_id, **kwargs):
        """
        met à jour les informations d'un véhicule.

        args:
            vehicule_id (int): id du véhicule à mettre à jour
            **kwargs: attributs à modifier

        returns:
            vehicule: véhicule mis à jour, ou none en cas d'erreur
        """
        try:
            # chargement du véhicule
            vehicule = self.db.charger_vehicule(vehicule_id)
            if not vehicule:
                return None

            # mise à jour des attributs communs
            attributs_communs = ['marque', 'modele', 'annee', 'kilometrage', 'prix_achat', 'cout_entretien_annuel']
            for attr in attributs_communs:
                if attr in kwargs:
                    setattr(vehicule, attr, kwargs[attr])

            # mise à jour des attributs spécifiques selon le type de véhicule
            if isinstance(vehicule, Voiture):
                attributs_specifiques = ['nb_places', 'puissance', 'carburant', 'options']
                for attr in attributs_specifiques:
                    if attr in kwargs:
                        setattr(vehicule, attr, kwargs[attr])

            elif isinstance(vehicule, Utilitaire):
                attributs_specifiques = ['volume', 'charge_utile', 'hayon']
                for attr in attributs_specifiques:
                    if attr in kwargs:
                        setattr(vehicule, attr, kwargs[attr])

            elif isinstance(vehicule, Moto):
                attributs_specifiques = ['cylindree', 'type_moto']
                for attr in attributs_specifiques:
                    if attr in kwargs:
                        setattr(vehicule, attr, kwargs[attr])

            # sauvegarde des modifications
            self.db.sauvegarder_vehicule(vehicule)

            # mise à jour du parc
            for i, v in enumerate(self.parc.vehicules):
                if v.id == vehicule_id:
                    self.parc.vehicules[i] = vehicule
                    break

            return vehicule

        except Exception as e:
            print(f"erreur lors de la mise à jour du véhicule: {e}")
            return None

    def obtenir_vehicule(self, vehicule_id):
        """
        récupère un véhicule par son id.

        args:
            vehicule_id (int): id du véhicule à récupérer

        returns:
            vehicule: véhicule trouvé, ou none si non trouvé
        """
        try:
            # recherche d'abord dans le parc (pour éviter d'interroger la base de données)
            for vehicule in self.parc.vehicules:
                if vehicule.id == vehicule_id:
                    return vehicule

            # si non trouvé dans le parc, interroger la base de données
            return self.db.charger_vehicule(vehicule_id)

        except Exception as e:
            print(f"erreur lors de la récupération du véhicule: {e}")
            return None

    def rechercher_vehicules(self, criteres=None):
        """
        recherche des véhicules selon certains critères.

        args:
            criteres (dict, optional): critères de recherche

        returns:
            list: liste des véhicules correspondant aux critères
        """
        try:
            return self.db.rechercher_vehicules(criteres)
        except Exception as e:
            print(f"erreur lors de la recherche de véhicules: {e}")
            return []

    def verifier_disponibilite(self, type_vehicule, criteres, date_debut, date_fin):
        """
        vérifie la disponibilité des véhicules pour une période donnée.

        args:
            type_vehicule (str): type de véhicule ('voiture', 'utilitaire', 'moto')
            criteres (dict): critères spécifiques
            date_debut (datetime): date de début de la période
            date_fin (datetime): date de fin de la période

        returns:
            list: liste des véhicules disponibles
        """
        try:
            return self.parc.verifier_disponibilite(type_vehicule, criteres, date_debut, date_fin)
        except Exception as e:
            print(f"erreur lors de la vérification de disponibilité: {e}")
            return []

    def verifier_disponibilite_vehicule(self, vehicule_id, date_debut, date_fin, reservation_id_a_exclure=None):
        """
        vérifie si un véhicule spécifique est disponible pour une période donnée.

        args:
            vehicule_id (int): id du véhicule
            date_debut (datetime): date de début de la période
            date_fin (datetime): date de fin de la période
            reservation_id_a_exclure (int, optional): id d'une réservation à exclure

        returns:
            bool: true si le véhicule est disponible, false sinon
        """
        try:
            # récupération du véhicule
            vehicule = self.obtenir_vehicule(vehicule_id)
            if not vehicule:
                return False

            # vérification des réservations existantes
            for reservation in self.parc.reservations:
                # ignorer la réservation à exclure
                if reservation_id_a_exclure and reservation.id == reservation_id_a_exclure:
                    continue

                # ignorer les réservations qui ne concernent pas ce véhicule
                if reservation.vehicule_id != vehicule_id:
                    continue

                # ignorer les réservations annulées
                if reservation.statut == "annulée":
                    continue

                # vérifier le chevauchement de périodes
                if not (reservation.date_fin < date_debut or reservation.date_debut > date_fin):
                    return False

            return True

        except Exception as e:
            print(f"erreur lors de la vérification de disponibilité: {e}")
            return False

    def optimiser_parc(self, historique_reservations=None, budget_annuel=None):
        """
        optimise le parc de véhicules en fonction de l'historique.

        args:
            historique_reservations (list, optional): historique des réservations
            budget_annuel (float, optional): budget disponible pour l'année

        returns:
            dict: recommandations d'optimisation
        """
        try:
            # si l'historique n'est pas fourni, le charger depuis la base de données
            if historique_reservations is None:
                # dans une implémentation complète, il faudrait implémenter cette méthode
                # historique_reservations = self.db.charger_historique_reservations()
                pass

            # exécuter l'algorithme d'optimisation
            return self.parc.optimiser_parc(historique_reservations, budget_annuel)

        except Exception as e:
            print(f"erreur lors de l'optimisation du parc: {e}")
            return None

    def obtenir_statistiques_parc(self):
        """
        calcule diverses statistiques sur le parc.

        returns:
            dict: statistiques du parc
        """
        try:
            # statistiques par type de véhicule
            stats_par_type = {
                "Voiture": 0,
                "Utilitaire": 0,
                "Moto": 0
            }

            # âge moyen par type
            age_total_par_type = {
                "Voiture": 0,
                "Utilitaire": 0,
                "Moto": 0
            }

            # valeur totale du parc
            valeur_totale = 0

            # année courante pour calculer l'âge
            annee_courante = datetime.now().year

            # parcours des véhicules
            for vehicule in self.parc.vehicules:
                # détermination du type
                if isinstance(vehicule, Voiture):
                    type_vehicule = "Voiture"
                elif isinstance(vehicule, Utilitaire):
                    type_vehicule = "Utilitaire"
                elif isinstance(vehicule, Moto):
                    type_vehicule = "Moto"
                else:
                    continue

                # incrémentation du compteur
                stats_par_type[type_vehicule] += 1

                # cumul de l'âge
                age_total_par_type[type_vehicule] += (annee_courante - vehicule.annee)

                # cumul de la valeur
                valeur_totale += vehicule.prix_achat

            # calcul des âges moyens
            age_moyen_par_type = {}
            for type_vehicule, total in age_total_par_type.items():
                if stats_par_type[type_vehicule] > 0:
                    age_moyen_par_type[type_vehicule] = total / stats_par_type[type_vehicule]
                else:
                    age_moyen_par_type[type_vehicule] = 0

            # construction du résultat
            statistiques = {
                "nombre_total_vehicules": sum(stats_par_type.values()),
                "repartition_par_type": stats_par_type,
                "age_moyen_par_type": age_moyen_par_type,
                "valeur_totale_parc": valeur_totale
            }

            return statistiques

        except Exception as e:
            print(f"erreur lors du calcul des statistiques: {e}")
            return {}


# exemple d'utilisation (ce code ne s'exécute que si on lance le fichier directement)
# exemple d'utilisation (ce code ne s'exécute que si on lance le fichier directement)
if __name__ == "__main__":
    from utils.database import Database

    # création d'une instance de la base de données
    db = Database("test_parc.db")

    # création du contrôleur
    parc_controller = ParcController(db)

    # ajout d'une voiture au parc
    nouvelle_voiture = parc_controller.ajouter_vehicule(
        type_vehicule="Voiture",
        marque="renault",
        modele="clio",
        annee=2020,
        kilometrage=15000,
        prix_achat=12000,
        cout_entretien_annuel=500,
        nb_places=5,
        puissance=90,
        carburant="essence",
        options=["climatisation", "bluetooth"]
    )

    if nouvelle_voiture:
        print(f"voiture ajoutée: {nouvelle_voiture.marque} {nouvelle_voiture.modele}")

        # modification de la voiture
        voiture_modifiee = parc_controller.mettre_a_jour_vehicule(
            nouvelle_voiture.id,
            kilometrage=18000
        )

        if voiture_modifiee:
            print(f"voiture modifiée: km = {voiture_modifiee.kilometrage}")

    # ajout d'un utilitaire
    nouvel_utilitaire = parc_controller.ajouter_vehicule(
        type_vehicule="Utilitaire",
        marque="citroën",
        modele="jumpy",
        annee=2019,
        kilometrage=30000,
        prix_achat=18000,
        cout_entretien_annuel=800,
        volume=8,
        charge_utile=1200
    )

    # calcul des statistiques du parc
    stats = parc_controller.obtenir_statistiques_parc()
    print(f"nombre total de véhicules: {stats['nombre_total_vehicules']}")
    print(f"répartition: {stats['repartition_par_type']}")

    # fermeture de la connexion à la base de données
    db.fermer()