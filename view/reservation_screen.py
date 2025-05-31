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

class ReservationScreen(QDialog):
    def __init__(self):
        super(ReservationScreen, self).__init__()
        loadUi('reservation.ui', self)

        # Initialisation de la base de données et des contrôleurs
        self.db = Database("../model/location.db")
        self.parc_controller = ParcController(self.db)
        self.reservation_controller = ReservationController(self.db, self.parc_controller)
        self.client_controller = ClientController(self.db)

        # Initialisation de l'interface
        self.typeBox.currentTextChanged.connect(self.on_type_change)
        self.searchButton.clicked.connect(self.rechercher)
        self.reserveButton.clicked.connect(self.reserver)

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

            # Recherche des véhicules disponibles via le contrôleur du parc
            vehicules_disponibles = self.parc_controller.verifier_disponibilite(
                type_vehicule, criteres, datetime_debut, datetime_fin
            )

            if not vehicules_disponibles:
                QMessageBox.information(self, "Aucun résultat", "Aucun véhicule disponible pour ces critères.")
                self._clear_table()
                return

            # Affichage des résultats
            self._afficher_vehicules(vehicules_disponibles, type_vehicule)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")
            self._clear_table()

    def _afficher_vehicules(self, vehicules, type_vehicule):
        """Affiche les véhicules dans le tableau"""
        # Détermination des colonnes selon le type de véhicule
        if type_vehicule == "Voiture":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Carburant", "Puissance", "Places"]
            attributs = ["id", "marque", "modele", "annee", "carburant", "puissance", "nb_places"]
        elif type_vehicule == "Utilitaire":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Volume", "Charge utile", "Hayon"]
            attributs = ["id", "marque", "modele", "annee", "volume", "charge_utile", "hayon"]
        elif type_vehicule == "Moto":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Cylindrée", "Type", ""]
            attributs = ["id", "marque", "modele", "annee", "cylindree", "type", ""]

        # Configuration du tableau
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(colonnes))
        self.tableWidget.setHorizontalHeaderLabels(colonnes)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        # Ajout des véhicules au tableau
        for vehicule in vehicules:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            for col, attribut in enumerate(attributs):
                if attribut:  # Si l'attribut n'est pas vide
                    valeur = getattr(vehicule, attribut, "")
                    if attribut == "hayon":
                        valeur = "Oui" if valeur else "Non"

                    item = QTableWidgetItem(str(valeur))
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # ← Ajout de cette ligne
                    self.tableWidget.setItem(row, col, item)
                else:
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # ← Ajout de cette ligne
                    self.tableWidget.setItem(row, col, item)

    def _clear_table(self):
        """Vide le tableau"""
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

    def reserver(self):
        """Bouton réserver - fonctionnalité à implémenter"""
        # Vérification qu'un véhicule est sélectionné
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Sélection requise", "Veuillez sélectionner un véhicule à réserver.")
            return

        # Pour l'instant, on affiche juste un message
        QMessageBox.information(self, "Réservation", "Fonctionnalité de réservation à implémenter.")

        # TODO: Implémenter la logique de réservation
        # - Récupérer l'ID du véhicule sélectionné
        # - Récupérer l'ID du client connecté
        # - Utiliser self.reservation_controller.creer_reservation()