from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QTableWidget, \
    QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate
from controller.parc_controller import ParcController
from controller.reservation_controller import ReservationController
from controller.client_controller import ClientController
from utils.database import Database
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QInputDialog,
    QAbstractItemView,
    QApplication
)
import re
from PyQt5.QtCore import QDate
from PyQt5.uic import loadUi

class ReservationScreen(QDialog):
    def __init__(self):
        super(ReservationScreen, self).__init__()
        loadUi('reservation.ui', self)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Initialisation de la base de données et des contrôleurs
        self.db = Database("../utils/test.db")
        self.parc_controller = ParcController(self.db)
        self.client_controller = ClientController(self.db)
        self.reservation_controller = ReservationController(self.db, self.parc_controller, self.client_controller)

        # Initialisation de l'interface
        self.typeBox.currentTextChanged.connect(self.on_type_change)
        self.searchButton.clicked.connect(self.rechercher)
        self.reserveButton.clicked.connect(self.reserver)
        # Connexion de la checkbox
        self.showUnavailableBox.stateChanged.connect(self.rechercher)

        # Configuration des dates par défaut
        self.startDate.setDate(QDate.currentDate())
        self.endDate.setDate(QDate.currentDate().addDays(1))

        # Chargement des types de véhicules
        self.load_types()

    def load_types(self):
        """Charge les types de véhicules disponibles"""
        self.typeBox.addItems(["Voiture", "Utilitaire", "Moto"])
        self.on_type_change("Voiture")

    def on_type_change(self, type_selected):
        """Met à jour les critères selon le type de véhicule sélectionné"""
        self.criteriaBox.clear()
        if type_selected == "Voiture":
            self.criteriaBox.addItems(["Puissance > 100", "Essence", "Diesel"])
        elif type_selected == "Utilitaire":
            self.criteriaBox.addItems(["Volume > 9 m³"])
        elif type_selected == "Moto":
            self.criteriaBox.addItems(["Cylindrée > 500"])

    def rechercher(self):
        """Recherche les véhicules disponibles selon les critères"""
        try:
            # Récupération des paramètres de recherche
            type_vehicule = self.typeBox.currentText()
            date_debut = self.startDate.date().toPyDate()
            date_fin = self.endDate.date().toPyDate()
            critere_selectionne = self.criteriaBox.currentText()

            # Conversion des dates Python en datetime
            datetime_debut = datetime.combine(date_debut, datetime.min.time())
            datetime_fin = datetime.combine(date_fin, datetime.min.time())

            # Construction des critères selon le type et la sélection
            criteres = {}
            if type_vehicule == "Voiture" and "Puissance" in critere_selectionne:
                criteres = {"puissance": {"min": 100}}
            elif type_vehicule == "Voiture" and critere_selectionne in ["Essence", "Diesel"]:
                criteres = {"carburant": critere_selectionne}
            elif type_vehicule == "Utilitaire" and "Volume" in critere_selectionne:
                criteres = {"volume": {"min": 9}}
            elif type_vehicule == "Moto" and "Cylindrée" in critere_selectionne:
                criteres = {"cylindree": {"min": 500}}

            # DEBUG: Avant la recherche de disponibilité
            print(f"DEBUG: Recherche pour véhicule type {type_vehicule}, dates {datetime_debut} à {datetime_fin}")
            print(f"DEBUG: Nombre total de réservations dans le parc: {len(self.parc_controller.parc.reservations)}")

            # Filtrage selon la checkbox
            if self.showUnavailableBox.isChecked():
                # Afficher tous les véhicules (disponibles + indisponibles)
                print("DEBUG: Affichage de tous les véhicules (disponibles + indisponibles)")
                tous_vehicules = self.parc_controller.rechercher_vehicules(criteres={"type": type_vehicule})
                vehicules_a_afficher = []
                for v in tous_vehicules:
                    if self._correspond_criteres(v, criteres):
                        vehicules_a_afficher.append(v)
            else:
                # Afficher seulement les disponibles (comportement actuel)
                print("DEBUG: Affichage seulement des véhicules disponibles")
                vehicules_a_afficher = self.parc_controller.verifier_disponibilite(
                    type_vehicule, criteres, datetime_debut, datetime_fin
                )

            if not vehicules_a_afficher:
                QMessageBox.information(self, "Aucun résultat", "Aucun véhicule trouvé pour ces critères.")
                self._clear_table()
                return

            # Affichage des résultats
            self._afficher_vehicules(vehicules_a_afficher, type_vehicule)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")
            self._clear_table()

    def _correspond_criteres(self, vehicule, criteres):
        """Vérifie si un véhicule correspond aux critères (copie de la logique du parc)"""
        if not criteres:
            return True

        for cle, valeur in criteres.items():
            if not hasattr(vehicule, cle):
                return False
            attr_valeur = getattr(vehicule, cle)

            if isinstance(valeur, dict):
                if "min" in valeur and attr_valeur < valeur["min"]:
                    return False
                if "max" in valeur and attr_valeur > valeur["max"]:
                    return False
            elif isinstance(attr_valeur, list) and isinstance(valeur, str):
                if valeur not in attr_valeur:
                    return False
            elif attr_valeur != valeur:
                return False

        return True


    def _afficher_vehicules(self, vehicules, type_vehicule):
        """Affiche les véhicules dans le tableau"""
        # Détermination des colonnes selon le type de véhicule
        if type_vehicule == "Voiture":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Carburant", "Puissance", "Places", "Disponible"]
            attributs = ["id", "marque", "modele", "annee", "carburant", "puissance", "nb_places", "disponible"]
        elif type_vehicule == "Utilitaire":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Volume", "Charge utile", "Hayon", "Disponible"]
            attributs = ["id", "marque", "modele", "annee", "volume", "charge_utile", "hayon", "disponible"]
        elif type_vehicule == "Moto":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Cylindrée", "Type", "Disponible"]
            attributs = ["id", "marque", "modele", "annee", "cylindree", "type", "disponible"]

        # Configuration du tableau
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(colonnes))
        self.tableWidget.setHorizontalHeaderLabels(colonnes)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        # Récupération des dates pour vérifier disponibilité
        date_debut = self.startDate.date().toPyDate()
        date_fin = self.endDate.date().toPyDate()
        datetime_debut = datetime.combine(date_debut, datetime.min.time())
        datetime_fin = datetime.combine(date_fin, datetime.min.time())

        # Ajout des véhicules au tableau
        for vehicule in vehicules:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            for col, attribut in enumerate(attributs):
                if attribut == "disponible":
                    # Vérification de disponibilité
                    disponible = self.parc_controller.verifier_disponibilite_vehicule(
                        vehicule.id, datetime_debut, datetime_fin
                    )
                    statut = "✅ Disponible" if disponible else "❌ Occupé"
                    item = QTableWidgetItem(statut)
                elif attribut:
                    valeur = getattr(vehicule, attribut, "")
                    if attribut == "hayon":
                        valeur = "Oui" if valeur else "Non"
                    item = QTableWidgetItem(str(valeur))
                else:
                    item = QTableWidgetItem("")

                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.tableWidget.setItem(row, col, item)

    def _clear_table(self):
        """Vide le tableau"""
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

    def reserver(self):
        """Créer une réservation pour le véhicule sélectionné"""
        try:
            # Vérifier qu'un véhicule est sélectionné
            current_row = self.tableWidget.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un véhicule à réserver")
                return

            # Récupérer l'ID du véhicule depuis le tableau
            vehicule_id = int(self.tableWidget.item(current_row, 0).text())

            # Récupérer les informations du véhicule pour l'affichage
            marque = self.tableWidget.item(current_row, 1).text()
            modele = self.tableWidget.item(current_row, 2).text()
            annee = self.tableWidget.item(current_row, 3).text()
            vehicule_info = f"{marque} {modele} ({annee})"

            # Récupérer les dates
            date_debut = self.startDate.date().toPyDate()
            date_fin = self.endDate.date().toPyDate()

            # Conversion en datetime
            datetime_debut = datetime.combine(date_debut, datetime.min.time())
            datetime_fin = datetime.combine(date_fin, datetime.min.time())

            # Validation des dates
            if datetime_debut >= datetime_fin:
                QMessageBox.warning(self, "Dates invalides", "La date de fin doit être postérieure à la date de début")
                return

            try:
                # Récupérer tous les clients depuis la base de données
                if hasattr(self, 'client_controller') and self.client_controller:
                    clients_disponibles = self.client_controller.lister_tous_clients()
                else:
                    # Fallback si pas de client_controller
                    clients_disponibles = []

                if not clients_disponibles:
                    # Si aucun client trouvé, permettre la saisie manuelle
                    client_id, ok = QInputDialog.getInt(
                        self,
                        "Client",
                        "Aucun client trouvé en base.\nEntrez manuellement l'ID du client:",
                        value=1,
                        min=1,
                        max=9999
                    )
                    if not ok:
                        return
                else:
                    # Créer une liste pour la ComboBox
                    items_clients = []
                    for client in clients_disponibles:
                        item_text = f"{client.prenom} {client.nom} (ID: {client.id})"
                        items_clients.append(item_text)

                    # Afficher la liste déroulante
                    client_choisi, ok = QInputDialog.getItem(
                        self,
                        "Sélection du client",
                        "Choisissez le client pour cette réservation:",
                        items_clients,
                        0,
                        False
                    )

                    if not ok:
                        return

                    # Extraire l'ID du texte sélectionné
                    # Format: "Prénom Nom (ID: 123)"
                    import re
                    match = re.search(r'\(ID: (\d+)\)', client_choisi)
                    if match:
                        client_id = int(match.group(1))
                    else:
                        QMessageBox.warning(self, "Erreur", "Impossible d'extraire l'ID du client")
                        return

                    print(f"DEBUG: Client sélectionné - ID: {client_id}, Texte: {client_choisi}")

            except Exception as e:
                print(f"DEBUG: Erreur lors de la récupération des clients: {e}")
                # Fallback vers saisie manuelle
                client_id, ok = QInputDialog.getInt(
                    self,
                    "Client",
                    f"Erreur de récupération des clients ({e}).\nEntrez manuellement l'ID:",
                    value=1,
                    min=1,
                    max=9999
                )
                if not ok:
                    return

            # DEBUG: Informations de réservation
            print(f"DEBUG: Tentative de réservation")
            print(f"  - Client ID: {client_id}")
            print(f"  - Véhicule ID: {vehicule_id} ({vehicule_info})")
            print(f"  - Dates: {datetime_debut} à {datetime_fin}")

            # Création de la réservation avec génération automatique de PDF
            resultat = self.reservation_controller.creer_reservation(
                client_id, vehicule_id, datetime_debut, datetime_fin
            )

            reservation = resultat['reservation']
            facture_pdf = resultat['facture_pdf']

            # DEBUG: Vérifier que la réservation est bien créée
            if reservation:
                print(f"DEBUG: Réservation créée - ID: {reservation.id}, Statut: {reservation.statut}")
                print(f"DEBUG: Véhicule {vehicule_id}, du {datetime_debut} au {datetime_fin}")

                # DEBUG: Vérifier les réservations dans le parc
                print(f"DEBUG: Nombre de réservations dans le parc: {len(self.parc_controller.parc.reservations)}")
                for res in self.parc_controller.parc.reservations:
                    if res.vehicule_id == vehicule_id:
                        print(
                            f"  - Réservation véhicule {res.vehicule_id}: {res.date_debut} à {res.date_fin}, statut: {res.statut}")

            if reservation:
                # Message de succès avec info sur la facture
                message = f"Réservation confirmée !\n\n"
                message += f"Numéro de réservation: {reservation.id}\n"
                message += f"Client ID: {client_id}\n"
                message += f"Véhicule: {vehicule_info}\n"
                message += f"Période: {datetime_debut.strftime('%d/%m/%Y')} au {datetime_fin.strftime('%d/%m/%Y')}\n"

                # Ajouter le prix si disponible
                if hasattr(reservation, 'prix') and reservation.prix:
                    message += f"Prix: {reservation.prix:.2f} €\n"

                # Information sur la facture PDF
                if facture_pdf:
                    message += f"\n✓ Facture PDF générée: {facture_pdf}"
                    message += f"\nLe fichier PDF a été sauvegardé dans le dossier de travail."
                else:
                    message += f"\n⚠ Facture PDF non générée (erreur technique)"

                QMessageBox.information(self, "Réservation confirmée", message)

                # Actualiser l'affichage pour voir les changements de disponibilité
                self.rechercher()

            else:
                QMessageBox.warning(self, "Erreur",
                                    "Impossible de créer la réservation.\n\n"
                                    "Vérifiez que:\n"
                                    "- Le client existe\n"
                                    "- Le véhicule est disponible\n"
                                    "- Les dates sont valides")

        except ValueError as e:
            QMessageBox.critical(self, "Erreur de saisie", f"Données invalides: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la réservation: {str(e)}")
            print(f"DEBUG: Erreur détaillée - {e}")
            import traceback
            traceback.print_exc()