# view/main2.py - Interface graphique pour la gestion des véhicules
import os
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QStackedWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QLabel, QWidget)
from PyQt5.QtGui import QPalette, QPixmap

# Ajouter le répertoire parent au chemin de recherche des modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Importation des modules du projet
from controller.parc_controller import ParcController
from utils.database import Database
from model.vehicule import Voiture, Utilitaire, Moto


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        self.setWindowTitle("Système de Location de Véhicules")
        self.setFixedSize(1200, 800)
        self.setObjectName("MainWindow")

        # Création du layout
        layout = QVBoxLayout()

        # Création d'un label pour le titre
        title = QLabel("Système de Location de Véhicules")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # Image de logo si disponible
        try:
            logo_path = os.path.join(parent_dir, 'logo.jpeg')
            if os.path.exists(logo_path):
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaled(400, 400, QtCore.Qt.KeepAspectRatio))
                logo_label.setAlignment(QtCore.Qt.AlignCenter)
                layout.addWidget(logo_label)
        except Exception as e:
            print(f"Erreur de chargement du logo: {e}")

        # Ajouter un espace
        layout.addStretch()

        # Bouton pour se connecter
        self.push = QPushButton("Se connecter")
        self.push.setFixedSize(200, 50)
        self.push.clicked.connect(self.gotologin)

        # Centrer le bouton
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.push)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        self.setWindowTitle("Connexion")
        self.setFixedSize(1200, 800)

        # Création du layout
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Connexion")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # Formulaire de connexion
        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        # Email
        self.emailfield = QLineEdit()
        self.emailfield.setPlaceholderText("Entrez votre email")
        form_layout.addRow(QLabel("Email:"), self.emailfield)

        # Mot de passe
        self.passwordfield = QLineEdit()
        self.passwordfield.setPlaceholderText("Entrez votre mot de passe")
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(QLabel("Mot de passe:"), self.passwordfield)

        # Centrer le formulaire
        form_container = QHBoxLayout()
        form_container.addStretch()
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        form_widget.setMinimumWidth(400)
        form_container.addWidget(form_widget)
        form_container.addStretch()

        layout.addLayout(form_container)
        layout.addSpacing(20)

        # Message d'erreur
        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")
        self.error.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.error)

        # Bouton de connexion
        self.push2 = QPushButton("Se connecter")
        self.push2.setFixedSize(200, 50)
        self.push2.clicked.connect(self.loginfunction)

        # Centrer le bouton
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.push2)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Veuillez remplir tous les champs.")
        else:
            # Pour la démonstration, nous acceptons n'importe quelle valeur
            # Dans une application réelle, vous vérifiriez ces informations dans la base de données
            self.error.setText("")
            vehicule_screen = VehiculeScreen()
            widget.addWidget(vehicule_screen)
            widget.setCurrentIndex(widget.currentIndex() + 1)


class VehiculeScreen(QDialog):
    def __init__(self):
        super(VehiculeScreen, self).__init__()
        self.setWindowTitle("Gestion des Véhicules")
        self.setFixedSize(1200, 800)

        # Initialisation de la base de données et du contrôleur de parc
        try:
            # Chemin vers le fichier de base de données (à ajuster selon l'emplacement réel)
            db_path = os.path.join(parent_dir, 'test_parc.db')

            # Si ce chemin n'existe pas, essayer d'autres chemins possibles
            if not os.path.exists(db_path):
                possible_paths = [
                    os.path.join(parent_dir, 'controller', 'test_parc.db'),
                    os.path.join(parent_dir, 'utils', 'test_parc.db'),
                    os.path.join(parent_dir, 'view', 'test_parc.db')
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        db_path = path
                        break

            # Initialiser la base de données et le contrôleur
            self.db = Database(db_path)
            self.parc_controller = ParcController(self.db)

        except Exception as e:
            QMessageBox.critical(self, "Erreur de connexion",
                                 f"Impossible de se connecter à la base de données:\n{str(e)}")
            # Créer une base de données en mémoire pour éviter les erreurs
            self.db = Database(":memory:")
            self.db._creer_tables()  # Assurez-vous que les tables existent
            self.parc_controller = ParcController(self.db)
            # Générer quelques données de test
            self.db.generer_donnees_test(2, 1, 1, 2)

        # Création du layout principal
        main_layout = QVBoxLayout()

        # Titre de la page
        title = QLabel("Gestion des Véhicules")
        title.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title)

        # Création du tableau des véhicules
        self.vehicule_table = QTableWidget()
        self.vehicule_table.setColumnCount(8)
        self.vehicule_table.setHorizontalHeaderLabels([
            "ID", "Type", "Marque", "Modèle", "Année",
            "Kilométrage", "Prix d'achat", "Attributs spécifiques"
        ])
        self.vehicule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vehicule_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vehicule_table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.vehicule_table)

        # Boutons pour ajouter et supprimer des véhicules
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Ajouter un véhicule")
        self.add_button.setMinimumWidth(150)
        self.add_button.clicked.connect(self.open_add_vehicule_dialog)

        self.delete_button = QPushButton("Supprimer le véhicule sélectionné")
        self.delete_button.setMinimumWidth(150)
        self.delete_button.clicked.connect(self.delete_vehicule)

        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Bouton pour revenir à l'écran précédent
        back_layout = QHBoxLayout()
        self.back_button = QPushButton("Retour")
        self.back_button.clicked.connect(self.go_back)
        back_layout.addWidget(self.back_button)
        back_layout.addStretch()

        main_layout.addLayout(back_layout)

        self.setLayout(main_layout)

        # Charger les véhicules
        self.load_vehicules()

    def load_vehicules(self):
        try:
            # Récupération de tous les véhicules
            vehicules = self.parc_controller.rechercher_vehicules()

            # Configuration du tableau
            self.vehicule_table.setRowCount(len(vehicules))

            # Remplissage du tableau
            for row, vehicule in enumerate(vehicules):
                # Attributs communs
                self.vehicule_table.setItem(row, 0, QTableWidgetItem(str(vehicule.id)))
                self.vehicule_table.setItem(row, 1, QTableWidgetItem(vehicule.__class__.__name__))
                self.vehicule_table.setItem(row, 2, QTableWidgetItem(vehicule.marque))
                self.vehicule_table.setItem(row, 3, QTableWidgetItem(vehicule.modele))
                self.vehicule_table.setItem(row, 4, QTableWidgetItem(str(vehicule.annee)))
                self.vehicule_table.setItem(row, 5, QTableWidgetItem(str(vehicule.kilometrage)))
                self.vehicule_table.setItem(row, 6, QTableWidgetItem(str(vehicule.prix_achat) + " €"))

                # Attributs spécifiques selon le type de véhicule
                if isinstance(vehicule, Voiture):
                    specific_attrs = f"Places: {vehicule.nb_places}, Puissance: {vehicule.puissance} ch, Carburant: {vehicule.carburant}"
                elif isinstance(vehicule, Utilitaire):
                    specific_attrs = f"Volume: {vehicule.volume} m³, Charge: {vehicule.charge_utile} kg, Hayon: {'Oui' if vehicule.hayon else 'Non'}"
                elif isinstance(vehicule, Moto):
                    specific_attrs = f"Cylindrée: {vehicule.cylindree} cm³, Type: {vehicule.type}"
                else:
                    specific_attrs = ""

                self.vehicule_table.setItem(row, 7, QTableWidgetItem(specific_attrs))

        except Exception as e:
            QMessageBox.warning(self, "Erreur de chargement",
                                f"Impossible de charger les véhicules:\n{str(e)}")

    def open_add_vehicule_dialog(self):
        dialog = AddVehiculeDialog(self.parc_controller)
        if dialog.exec_():
            # Recharger les véhicules après l'ajout
            self.load_vehicules()

    def delete_vehicule(self):
        selected_rows = self.vehicule_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Avertissement",
                                "Veuillez sélectionner un véhicule à supprimer.")
            return

        # Récupérer l'ID du véhicule sélectionné
        row = selected_rows[0].row()
        vehicule_id = int(self.vehicule_table.item(row, 0).text())

        # Confirmation de suppression
        reply = QMessageBox.question(self, "Confirmation",
                                     f"Êtes-vous sûr de vouloir supprimer le véhicule #{vehicule_id} ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Tenter de supprimer le véhicule
            if self.parc_controller.retirer_vehicule(vehicule_id):
                QMessageBox.information(self, "Succès",
                                        "Le véhicule a été supprimé avec succès.")
                self.load_vehicules()  # Recharger le tableau
            else:
                QMessageBox.critical(self, "Erreur",
                                     "Impossible de supprimer ce véhicule. Il peut avoir des réservations actives.")

    def go_back(self):
        # Retourner à l'écran précédent
        widget.setCurrentIndex(widget.currentIndex() - 1)


class AddVehiculeDialog(QDialog):
    def __init__(self, parc_controller):
        super(AddVehiculeDialog, self).__init__()
        self.parc_controller = parc_controller
        self.setWindowTitle("Ajouter un véhicule")
        self.setMinimumWidth(500)

        # Layout principal
        self.layout = QVBoxLayout()

        # Titre
        title = QLabel("Ajouter un nouveau véhicule")
        title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title)

        # Formulaire pour les attributs communs
        common_form = QFormLayout()
        common_form.setSpacing(10)

        # Type de véhicule
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Voiture", "Utilitaire", "Moto"])
        self.type_combo.currentIndexChanged.connect(self.update_specific_form)
        common_form.addRow(QLabel("Type:"), self.type_combo)

        # Marque
        self.marque_input = QLineEdit()
        common_form.addRow(QLabel("Marque:"), self.marque_input)

        # Modèle
        self.modele_input = QLineEdit()
        common_form.addRow(QLabel("Modèle:"), self.modele_input)

        # Année
        self.annee_input = QSpinBox()
        self.annee_input.setRange(1900, 2025)
        self.annee_input.setValue(2023)
        common_form.addRow(QLabel("Année:"), self.annee_input)

        # Kilométrage
        self.km_input = QSpinBox()
        self.km_input.setRange(0, 1000000)
        self.km_input.setSingleStep(1000)
        common_form.addRow(QLabel("Kilométrage:"), self.km_input)

        # Prix d'achat
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 1000000)
        self.prix_input.setSingleStep(1000)
        self.prix_input.setSuffix(" €")
        common_form.addRow(QLabel("Prix d'achat:"), self.prix_input)

        # Coût d'entretien annuel
        self.entretien_input = QDoubleSpinBox()
        self.entretien_input.setRange(0, 10000)
        self.entretien_input.setSingleStep(100)
        self.entretien_input.setSuffix(" €")
        common_form.addRow(QLabel("Coût d'entretien annuel:"), self.entretien_input)

        # Ajout du formulaire commun au layout principal
        self.layout.addLayout(common_form)

        # Layout pour les attributs spécifiques
        self.specific_layout = QFormLayout()
        self.specific_layout.setSpacing(10)
        self.layout.addLayout(self.specific_layout)

        # Initialisation des inputs spécifiques
        self.init_specific_inputs()

        # Boutons de validation
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_vehicule)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Initialiser le formulaire spécifique
        self.update_specific_form()

    def init_specific_inputs(self):
        # Voiture
        self.nb_places_input = QSpinBox()
        self.nb_places_input.setRange(1, 9)
        self.nb_places_input.setValue(5)

        self.puissance_input = QSpinBox()
        self.puissance_input.setRange(0, 500)
        self.puissance_input.setValue(100)

        self.carburant_input = QComboBox()
        self.carburant_input.addItems(["Essence", "Diesel", "Hybride", "Électrique"])

        # Utilitaire
        self.volume_input = QDoubleSpinBox()
        self.volume_input.setRange(0, 50)
        self.volume_input.setSingleStep(0.5)
        self.volume_input.setValue(8)
        self.volume_input.setSuffix(" m³")

        self.charge_input = QSpinBox()
        self.charge_input.setRange(0, 5000)
        self.charge_input.setSingleStep(100)
        self.charge_input.setValue(1000)
        self.charge_input.setSuffix(" kg")

        self.hayon_input = QCheckBox()

        # Moto
        self.cylindree_input = QSpinBox()
        self.cylindree_input.setRange(50, 2000)
        self.cylindree_input.setSingleStep(50)
        self.cylindree_input.setValue(600)
        self.cylindree_input.setSuffix(" cm³")

        self.type_moto_input = QComboBox()
        self.type_moto_input.addItems(["Roadster", "Sportive", "Trail", "Routière"])

    def update_specific_form(self):
        # Effacer le formulaire spécifique
        for i in reversed(range(self.specific_layout.count())):
            item = self.specific_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Titre de section
        specific_title = QLabel("Caractéristiques spécifiques")
        self.specific_layout.addRow(specific_title, QWidget())

        # Ajouter les champs spécifiques selon le type sélectionné
        vehicule_type = self.type_combo.currentText()

        if vehicule_type == "Voiture":
            self.specific_layout.addRow(QLabel("Nombre de places:"), self.nb_places_input)
            self.specific_layout.addRow(QLabel("Puissance (ch):"), self.puissance_input)
            self.specific_layout.addRow(QLabel("Carburant:"), self.carburant_input)

        elif vehicule_type == "Utilitaire":
            self.specific_layout.addRow(QLabel("Volume:"), self.volume_input)
            self.specific_layout.addRow(QLabel("Charge utile:"), self.charge_input)
            self.specific_layout.addRow(QLabel("Hayon élévateur:"), self.hayon_input)

        elif vehicule_type == "Moto":
            self.specific_layout.addRow(QLabel("Cylindrée:"), self.cylindree_input)
            self.specific_layout.addRow(QLabel("Type:"), self.type_moto_input)

    def save_vehicule(self):
        # Vérifier que tous les champs obligatoires sont remplis
        if not self.marque_input.text() or not self.modele_input.text():
            QMessageBox.warning(self, "Champs obligatoires",
                                "Veuillez remplir tous les champs obligatoires.")
            return

        # Récupérer les valeurs communes
        common_args = {
            "marque": self.marque_input.text(),
            "modele": self.modele_input.text(),
            "annee": self.annee_input.value(),
            "kilometrage": self.km_input.value(),
            "prix_achat": self.prix_input.value(),
            "cout_entretien_annuel": self.entretien_input.value()
        }

        # Récupérer le type de véhicule
        vehicule_type = self.type_combo.currentText()

        # Ajouter les attributs spécifiques
        if vehicule_type == "Voiture":
            common_args.update({
                "nb_places": self.nb_places_input.value(),
                "puissance": self.puissance_input.value(),
                "carburant": self.carburant_input.currentText(),
                "options": []  # Liste vide par défaut
            })

        elif vehicule_type == "Utilitaire":
            common_args.update({
                "volume": self.volume_input.value(),
                "charge_utile": self.charge_input.value(),
                "hayon": self.hayon_input.isChecked()
            })

        elif vehicule_type == "Moto":
            common_args.update({
                "cylindree": self.cylindree_input.value(),
                "type_moto": self.type_moto_input.currentText()
            })

        try:
            # Appel au contrôleur pour ajouter le véhicule
            vehicule = self.parc_controller.ajouter_vehicule(vehicule_type, **common_args)

            if vehicule:
                QMessageBox.information(self, "Succès",
                                        f"Le {vehicule_type.lower()} a été ajouté avec succès.")
                self.accept()  # Fermer la boîte de dialogue
            else:
                QMessageBox.critical(self, "Erreur",
                                     "Une erreur est survenue lors de l'ajout du véhicule.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de l'ajout du véhicule:\n{str(e)}")


# Initialisation de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()
    widget = QStackedWidget()
    widget.addWidget(welcome)
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    widget.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Fermeture de l'application")