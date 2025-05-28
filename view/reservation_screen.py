from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate
from controller.parc_controller import ParcController
from controller.reservation_controller import ReservationController
from utils.database import Database
import datetime

class ReservationScreen(QDialog):
    def __init__(self):
        super(ReservationScreen, self).__init__()
        loadUi('reservation.ui', self)

        # Initialisation contrôleurs
        self.db = Database("test.db")
        self.parc_controller = ParcController(self.db)
        self.res_controller = ReservationController(self.db)

        # Initialisation interface
        self.typeBox.currentTextChanged.connect(self.on_type_change)
        self.searchButton.clicked.connect(self.rechercher)
        self.reserveButton.clicked.connect(self.reserver)

        self.startDate.setDate(QDate.currentDate())
        self.endDate.setDate(QDate.currentDate().addDays(1))
        self.load_types()

    def load_types(self):
        self.typeBox.addItems(["Voiture", "Utilitaire", "Moto"])
        self.on_type_change("Voiture")

    def on_type_change(self, type_selected):
        self.criteriaBox.clear()
        if type_selected == "Voiture":
            self.criteriaBox.addItems(["Puissance > 100", "Essence", "Diesel"])
        elif type_selected == "Utilitaire":
            self.criteriaBox.addItems(["Volume > 9 m³"])
        elif type_selected == "Moto":
            self.criteriaBox.addItems(["Cylindrée > 500"])

    def rechercher(self):
        type_v = self.typeBox.currentText()
        debut = self.startDate.date().toPyDate()
        fin = self.endDate.date().toPyDate()

        # Requête des véhicules filtrés
        vehicules = self.parc_controller.rechercher_vehicules(type_recherche=type_v)

        # Ici on filtre manuellement selon les critères simples
        critere = self.criteriaBox.currentText()

        if type_v == "Voiture" and "Puissance" in critere:
            vehicules = [v for v in vehicules if hasattr(v, 'puissance') and v.puissance > 100]
        elif type_v == "Utilitaire" and "Volume" in critere:
            vehicules = [v for v in vehicules if hasattr(v, 'volume') and v.volume >= 9]
        elif type_v == "Moto" and "Cylindrée" in critere:
            vehicules = [v for v in vehicules if hasattr(v, 'cylindree') and v.cylindree >= 500]

        # Affichage dans la table
        self.tableWidget.setRowCount(0)
        for v in vehicules:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(v.id)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(v.marque))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(v.modele))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(v.annee)))

    def reserver(self):
        selected = self.tableWidget.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Alerte", "Veuillez sélectionner un véhicule.")
            return

        id_vehicule = int(self.tableWidget.item(selected, 0).text())
        debut = self.startDate.date().toPyDate()
        fin = self.endDate.date().toPyDate()

        # Pour test : client fictif
        id_client = 1  # à lier plus tard avec session utilisateur

        try:
            self.res_controller.effectuer_reservation(id_client, id_vehicule, debut, fin)
            QMessageBox.information(self, "Succès", "Réservation effectuée avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec de la réservation : {str(e)}")
