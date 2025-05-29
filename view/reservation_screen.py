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
        try:
            type_v = self.typeBox.currentText()
            debut = self.startDate.date().toPyDate()
            fin = self.endDate.date().toPyDate()

            vehicules = self.parc_controller.rechercher_vehicules(criteres={"type": type_v})

            if not vehicules:
                QMessageBox.information(self, "Aucun résultat", "Aucun véhicule trouvé.")
                return

            critere = self.criteriaBox.currentText()
            if type_v == "Voiture" and "Puissance" in critere:
                vehicules = [v for v in vehicules if hasattr(v, 'puissance') and v.puissance > 100]
            elif type_v == "Utilitaire" and "Volume" in critere:
                vehicules = [v for v in vehicules if hasattr(v, 'volume') and v.volume >= 9]
            elif type_v == "Moto" and "Cylindrée" in critere:
                vehicules = [v for v in vehicules if hasattr(v, 'cylindree') and v.cylindree >= 500]

            dernier_attribut = ""
            dernier_label = ""

            if type_v == "Voiture":
                dernier_label = "Puissance"
                dernier_attribut = "puissance"
            elif type_v == "Utilitaire":
                dernier_label = "Volume"
                dernier_attribut = "volume"
            elif type_v == "Moto":
                dernier_label = "Cylindrée"
                dernier_attribut = "cylindree"

            # Configure les colonnes
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(7)
            self.tableWidget.setHorizontalHeaderLabels(["ID", "Marque", "Modèle", "Année", "Carburant", dernier_label, "Disponible"])
            self.tableWidget.horizontalHeader().setStretchLastSection(True)

            # Affichage dynamique
            for v in vehicules:
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(getattr(v, "id", ""))))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(getattr(v, "marque", "")))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(getattr(v, "modele", "")))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(str(getattr(v, "annee", ""))))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(getattr(v, "carburant", "-")))
                self.tableWidget.setItem(row, 5, QTableWidgetItem(str(getattr(v, dernier_attribut, "-"))))
                # Vérification de disponibilité
                disponible = self.parc_controller.verifier_disponibilite_vehicule(
                    v.id, debut, fin
                )

                etat = "✅" if disponible else "❌"
                self.tableWidget.setItem(row, 6, QTableWidgetItem(etat))



        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")

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
