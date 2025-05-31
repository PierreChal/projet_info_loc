# controller/reservation_controller.py
# ce fichier gère les opérations liées à la réservation de véhicules
# il fait partie de l'architecture MVC (modèle-vue-contrôleur)
#
# structure:
# - importe le modèle reservation et utilise datetime pour la gestion des dates
# - définit la classe reservationcontroller avec méthodes pour créer, annuler, terminer et modifier des réservations
# - implémente la vérification de disponibilité et la validation des données
# - permet de récupérer les détails complets d'une réservation (client et véhicule associés)
#
# interactions:
# - utilise le modèle reservation pour représenter les données
# - dépend du parccontroller pour vérifier la disponibilité des véhicules
# - communique avec la base de données pour persistance des informations
# - fournit aux vues les informations nécessaires pour afficher les réservations
# - sert d'intermédiaire entre les vues et les modèles client, véhicule et réservation

from datetime import datetime
from model.reservation import Reservation


class ReservationController:
    """
    contrôleur pour gérer les opérations liées aux réservations.
    fait le lien entre la vue et les modèles reservation, client et vehicule.

    attributes:
        db (database): instance de la base de données
        parc_controller: référence au contrôleur du parc

    author:
        [votre nom]
    """

    def __init__(self, db, parc_controller=None, client_controller=None):
        """
        initialise le contrôleur avec une connexion à la base de données.

        args:
            db (database): instance de la base de données
            parc_controller: référence au contrôleur du parc (optionnel)
        """
        self.db = db
        self.parc_controller = parc_controller
        self.client_controller = client_controller

    def creer_reservation(self, client_id, vehicule_id, date_debut, date_fin):
        """
        crée une nouvelle réservation et génère automatiquement la facture PDF.

        args:
            client_id (int): id du client
            vehicule_id (int): id du véhicule
            date_debut (datetime): date de début de la réservation
            date_fin (datetime): date de fin de la réservation

        returns:
            dict: {
                'reservation': réservation créée,
                'facture_pdf': chemin du fichier PDF généré (ou None en cas d'erreur)
            }
        """
        try:
            # validation des données
            if not self._valider_donnees_reservation(client_id, vehicule_id, date_debut, date_fin):
                return {'reservation': None, 'facture_pdf': None}

            # vérification de la disponibilité du véhicule
            if self.parc_controller and not self._verifier_disponibilite(vehicule_id, date_debut, date_fin):
                print("le véhicule n'est pas disponible pour cette période")
                return {'reservation': None, 'facture_pdf': None}

            # création de l'objet réservation
            nouvelle_reservation = Reservation(
                id=None,
                client_id=client_id,
                vehicule_id=vehicule_id,
                date_debut=date_debut,
                date_fin=date_fin,
                statut="confirmée"
            )

            # calcul du prix si possible
            if self.parc_controller:
                vehicule = self.parc_controller.obtenir_vehicule(vehicule_id)
                if vehicule:
                    nouvelle_reservation.calculer_prix(vehicule)

            # sauvegarde dans la base de données
            reservation_id = self.db.sauvegarder_reservation(nouvelle_reservation)

            # récupération de la réservation complète
            reservation_complete = self.db.charger_reservation(reservation_id)

            # AJOUT : Ajouter la réservation au parc en mémoire
            if self.parc_controller and reservation_complete:
                self.parc_controller.parc.reservations.append(reservation_complete)
                print(f"Réservation ajoutée au parc. Total réservations: {len(self.parc_controller.parc.reservations)}")

            # NOUVEAU : Génération automatique de la facture PDF
            facture_pdf_path = None
            if reservation_complete:
                try:
                    facture_pdf_path = self._generer_facture_pdf(reservation_complete)
                    print(f"✓ Facture PDF générée: {facture_pdf_path}")
                except Exception as e:
                    print(f"⚠ Erreur lors de la génération de la facture PDF: {e}")

            return {
                'reservation': reservation_complete,
                'facture_pdf': facture_pdf_path
            }

        except Exception as e:
            print(f"erreur lors de la création de la réservation: {e}")
            return {'reservation': None, 'facture_pdf': None}

    def _generer_facture_pdf(self, reservation):
        """
        Génère une facture PDF pour une réservation.

        args:
            reservation: objet réservation

        returns:
            str: chemin du fichier PDF généré
        """
        try:
            # Import des modules nécessaires
            from datetime import datetime
            from utils.pdf_generator import PDFGenerator
            from model.facture import Facture

            # Récupération des données nécessaires
            client = self.client_controller.charger_client(reservation.client_id) if self.client_controller else None
            vehicule = self.parc_controller.obtenir_vehicule(reservation.vehicule_id) if self.parc_controller else None

            if not client or not vehicule:
                raise Exception("Impossible de récupérer les données client ou véhicule")

            # Création de l'objet Facture
            facture = Facture(
                id=f"F{reservation.id}",
                reservation_id=reservation.id,
                date_emission=datetime.now(),
                montant_ht=reservation.prix if hasattr(reservation, 'prix') else 100.0,
                taux_tva=0.2
            )

            # Calcul du montant TTC
            facture.montant_ttc = facture.montant_ht * (1 + facture.taux_tva)

            # Génération du PDF
            chemin_pdf = PDFGenerator.generer_facture(facture, client, vehicule, reservation)

            return chemin_pdf

        except Exception as e:
            print(f"Erreur lors de la génération de la facture PDF: {e}")
            raise e

    def annuler_reservation(self, reservation_id):
        """
        annule une réservation existante.

        args:
            reservation_id (int): id de la réservation à annuler

        returns:
            bool: true si l'annulation a réussi, false sinon
        """
        try:
            # chargement de la réservation
            reservation = self.db.charger_reservation(reservation_id)
            if not reservation:
                return False

            # tentative d'annulation
            if not reservation.annuler():
                return False

            # sauvegarde des modifications
            self.db.sauvegarder_reservation(reservation)
            return True

        except Exception as e:
            print(f"erreur lors de l'annulation de la réservation: {e}")
            return False

    def terminer_reservation(self, reservation_id):
        """
        marque une réservation comme terminée.

        args:
            reservation_id (int): id de la réservation à terminer

        returns:
            bool: true si la terminaison a réussi, false sinon
        """
        try:
            # chargement de la réservation
            reservation = self.db.charger_reservation(reservation_id)
            if not reservation:
                return False

            # tentative de terminaison
            if not reservation.terminer():
                return False

            # sauvegarde des modifications
            self.db.sauvegarder_reservation(reservation)
            return True

        except Exception as e:
            print(f"erreur lors de la terminaison de la réservation: {e}")
            return False

    def modifier_dates_reservation(self, reservation_id, nouvelle_date_debut, nouvelle_date_fin):
        """
        modifie les dates d'une réservation existante.

        args:
            reservation_id (int): id de la réservation à modifier
            nouvelle_date_debut (datetime): nouvelle date de début
            nouvelle_date_fin (datetime): nouvelle date de fin

        returns:
            reservation: réservation modifiée, ou none en cas d'erreur
        """
        try:
            # chargement de la réservation
            reservation = self.db.charger_reservation(reservation_id)
            if not reservation or reservation.statut != "confirmée":
                return None

            # validation des nouvelles dates
            if nouvelle_date_debut >= nouvelle_date_fin:
                print("la date de fin doit être postérieure à la date de début")
                return None

            # vérification de la disponibilité du véhicule pour les nouvelles dates
            # on exclut la réservation actuelle de la vérification
            if self.parc_controller and not self._verifier_disponibilite(
                    reservation.vehicule_id,
                    nouvelle_date_debut,
                    nouvelle_date_fin,
                    reservation_id
            ):
                print("le véhicule n'est pas disponible pour cette nouvelle période")
                return None

            # anciennes dates (pour recalculer le prix)
            ancienne_date_debut = reservation.date_debut
            ancienne_date_fin = reservation.date_fin

            # mise à jour des dates
            reservation.date_debut = nouvelle_date_debut
            reservation.date_fin = nouvelle_date_fin

            # recalcul du prix si la durée a changé
            if (nouvelle_date_fin - nouvelle_date_debut).days != (ancienne_date_fin - ancienne_date_debut).days:
                if self.parc_controller:
                    vehicule = self.parc_controller.obtenir_vehicule(reservation.vehicule_id)
                    if vehicule:
                        reservation.calculer_prix(vehicule)

            # sauvegarde des modifications
            self.db.sauvegarder_reservation(reservation)

            # récupération de la réservation mise à jour
            return self.db.charger_reservation(reservation_id)

        except Exception as e:
            print(f"erreur lors de la modification de la réservation: {e}")
            return None

    def obtenir_reservation(self, reservation_id):
        """
        récupère une réservation par son id.

        args:
            reservation_id (int): id de la réservation à récupérer

        returns:
            reservation: réservation trouvée, ou none si non trouvée
        """
        try:
            return self.db.charger_reservation(reservation_id)
        except Exception as e:
            print(f"erreur lors de la récupération de la réservation: {e}")
            return None

    def rechercher_reservations(self, criteres=None):
        """
        recherche des réservations selon certains critères.

        args:
            criteres (dict, optional): critères de recherche (client_id, vehicule_id, statut, etc.)

        returns:
            list: liste des réservations correspondant aux critères
        """
        try:
            # dans une implémentation complète, il faudrait développer cette méthode
            # en fonction des capacités de recherche de la base de données
            pass
        except Exception as e:
            print(f"erreur lors de la recherche de réservations: {e}")
            return []

    def obtenir_details_complets(self, reservation_id):
        """
        récupère tous les détails d'une réservation (client, véhicule, etc.).

        args:
            reservation_id (int): id de la réservation

        returns:
            dict: dictionnaire contenant tous les détails de la réservation
        """
        try:
            # chargement de la réservation
            reservation = self.db.charger_reservation(reservation_id)
            if not reservation:
                return None

            # chargement du client
            client = self.db.charger_client(reservation.client_id)

            # chargement du véhicule
            vehicule = None
            if self.parc_controller:
                vehicule = self.parc_controller.obtenir_vehicule(reservation.vehicule_id)
            else:
                vehicule = self.db.charger_vehicule(reservation.vehicule_id)

            # construction du dictionnaire de détails
            details = {
                "reservation": reservation,
                "client": client,
                "vehicule": vehicule,
                "duree_jours": reservation.duree_en_jours(),
                "prix_total": reservation.prix_total
            }

            return details

        except Exception as e:
            print(f"erreur lors de la récupération des détails de la réservation: {e}")
            return None

    def _valider_donnees_reservation(self, client_id, vehicule_id, date_debut, date_fin):
        """
        valide les données d'une réservation.

        args:
            client_id (int): id du client
            vehicule_id (int): id du véhicule
            date_debut (datetime): date de début de la réservation
            date_fin (datetime): date de fin de la réservation

        returns:
            bool: true si les données sont valides, false sinon
        """
        # vérification des identifiants
        if not client_id or not vehicule_id:
            print("les identifiants client et véhicule sont obligatoires")
            return False

        # vérification de l'existence du client
        client = self.db.charger_client(client_id)
        if not client:
            print(f"client {client_id} non trouvé")
            return False

        # vérification de l'existence du véhicule
        vehicule = None
        if self.parc_controller:
            vehicule = self.parc_controller.obtenir_vehicule(vehicule_id)
        else:
            vehicule = self.db.charger_vehicule(vehicule_id)

        if not vehicule:
            print(f"véhicule {vehicule_id} non trouvé")
            return False

        # vérification des dates
        if not date_debut or not date_fin:
            print("les dates de début et de fin sont obligatoires")
            return False

        if date_debut >= date_fin:
            print("la date de fin doit être postérieure à la date de début")
            return False

        # vérification que la date de début est dans le futur
        if date_debut.date() < datetime.now().date():
            print("la date de début ne peut pas être dans le passé")
            return False

        return True

    def _verifier_disponibilite(self, vehicule_id, date_debut, date_fin, reservation_id_a_exclure=None):
        """
        vérifie si un véhicule est disponible pour une période donnée.

        args:
            vehicule_id (int): id du véhicule
            date_debut (datetime): date de début de la période
            date_fin (datetime): date de fin de la période
            reservation_id_a_exclure (int, optional): id d'une réservation à exclure de la vérification

        returns:
            bool: true si le véhicule est disponible, false sinon
        """
        # si le contrôleur de parc est disponible, utiliser sa méthode
        if self.parc_controller:
            return self.parc_controller.verifier_disponibilite_vehicule(
                vehicule_id, date_debut, date_fin, reservation_id_a_exclure
            )

        # sinon, vérification manuelle à partir des réservations
        reservations = self.db.charger_reservations_vehicule(vehicule_id)

        for reservation in reservations:
            # ignorer la réservation à exclure
            if reservation_id_a_exclure and reservation.id == reservation_id_a_exclure:
                continue

            # ignorer les réservations annulées
            if reservation.statut == "annulée":
                continue

            # vérifier le chevauchement de périodes
            if not (reservation.date_fin < date_debut or reservation.date_debut > date_fin):
                return False

        return True


# exemple d'utilisation (ce code ne s'exécute que si on lance le fichier directement)
if __name__ == "__main__":
    from utils.database import Database
    from controller.parc_controller import ParcController
    from datetime import datetime, timedelta

    # création d'une instance de la base de données
    db = Database("test_reservation.db")

    # création des contrôleurs
    parc_controller = ParcController(db)
    reservation_controller = ReservationController(db, parc_controller)

    # dates pour les tests
    aujourd_hui = datetime.now()
    debut = aujourd_hui + timedelta(days=3)
    fin = aujourd_hui + timedelta(days=7)

    # création d'un client pour le test
    from model.client import Client

    client = Client(id=None, nom="durand", prenom="marie", adresse="1 rue des lilas, brest",
                    telephone="06 12 34 56 78", email="marie.durand@example.com")
    client_id = db.sauvegarder_client(client)
    print(f"client créé: {client.prenom} {client.nom}")

    # création d'un véhicule pour le test
    vehicule = parc_controller.ajouter_vehicule(
        type_vehicule="Voiture",
        marque="peugeot",
        modele="208",
        annee=2021,
        kilometrage=12000,
        prix_achat=15000,
        cout_entretien_annuel=600,
        nb_places=5,
        puissance=110,
        carburant="essence"
    )
    print(f"véhicule ajouté: {vehicule.marque} {vehicule.modele}")

    # création d'une réservation
    reservation = reservation_controller.creer_reservation(
        client_id=client_id,
        vehicule_id=vehicule.id,
        date_debut=debut,
        date_fin=fin
    )

    if reservation:
        print(
            f"réservation créée: du {reservation.date_debut.strftime('%d/%m/%Y')} au {reservation.date_fin.strftime('%d/%m/%Y')}")

        # modification des dates de la réservation
        nouvelle_date_debut = debut + timedelta(days=1)
        nouvelle_date_fin = fin + timedelta(days=2)

        reservation_modifiee = reservation_controller.modifier_dates_reservation(
            reservation.id,
            nouvelle_date_debut,
            nouvelle_date_fin
        )

        if reservation_modifiee:
            print(
                f"réservation modifiée: nouvelles dates du {reservation_modifiee.date_debut.strftime('%d/%m/%Y')} au {reservation_modifiee.date_fin.strftime('%d/%m/%Y')}")

        # récupération des détails complets
        details = reservation_controller.obtenir_details_complets(reservation.id)
        if details:
            print(
                f"détails de la réservation: {details['client'].prenom} {details['client'].nom} a réservé {details['vehicule'].marque} {details['vehicule'].modele}")
            print(f"durée: {details['duree_jours']} jours, prix total: {details['prix_total']} €")

        # annulation de la réservation
        if reservation_controller.annuler_reservation(reservation.id):
            print("réservation annulée avec succès")

            # vérification du statut
            reservation_annulee = reservation_controller.obtenir_reservation(reservation.id)
            print(f"statut de la réservation: {reservation_annulee.statut}")

    # fermeture de la connexion à la base de données
    db.fermer()