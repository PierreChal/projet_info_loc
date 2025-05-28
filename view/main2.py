import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QStackedWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QHeaderView
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
import sqlite3

# Import des classes du MVC existant
from utils.database import Database
from controller.parc_controller import ParcController
from model.vehicule import Voiture, Utilitaire, Moto


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi('welcomescreen.ui', self)
        self.setWindowTitle("Image en fond d'écran")
        self.setFixedSize(1200, 800)
        self.setObjectName("MainWindow")
        self.setStyleSheet("""
                    #MainWindow {
                        background-image: url('logo.jpeg');
                        background-repeat: no-repeat;
                        background-position: center;
                        background-attachment: fixed;
                    }
                """)
        self.push.clicked.connect(self.gotologin)
        self.push2.clicked.connect(self.gotocreate)
        self.pushButton_3.clicked.connect(self.gotoadmin)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoadmin(self):
        go = AdminScreen()
        widget.addWidget(go)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi('login.ui', self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.connexion.clicked.connect(self.loginfunction)
        self.back_to_home.clicked.connect(self.gotoaccueil)

    def gotoaccueil(self):
        widget.setCurrentIndex(0)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.erreur.setText("Merci de remplir tous les champs.")

        else:
            conn = sqlite3.connect("utilisateurs_data.db")
            cur = conn.cursor()
            try:
                cur.execute("SELECT MP FROM login_info WHERE Email = ?", (user,))
                result = cur.fetchone()

                if result is None:
                    self.erreur.setText("Cet identifiant n'existe pas.")
                elif result[0] == password:
                    print("Connecté avec succès.")
                    self.erreur.setText("")

                    # Après connexion réussie, afficher la page de visualisation des véhicules (déplacé côté admin)
                    # vehicules_screen = VehiculesScreen()
                    # widget.addWidget(vehicules_screen)
                    # widget.setCurrentIndex(widget.currentIndex() + 1)
                else:
                    self.erreur.setText("Mot de passe incorrect.")
            except Exception as e:
                self.erreur.setText("Erreur : " + str(e))
            finally:
                conn.close()

class AdminScreen(QDialog):
    def __init__(self):
        super(AdminScreen, self).__init__()
        loadUi('admiN.ui', self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.connexion.clicked.connect(self.loginfunction)
        self.back_to_home.clicked.connect(self.gotoaccueil)

    def gotoaccueil(self):
        widget.setCurrentIndex(0)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.erreur.setText("Merci de remplir tous les champs.")

        else:
            conn = sqlite3.connect("gestionnaires_data.db")
            cur = conn.cursor()
            try:
                cur.execute("SELECT MP FROM GESTIONNAIRES WHERE Email = ?", (user,))
                result = cur.fetchone()

                if result is None:
                    self.erreur.setText("Cet identifiant n'existe pas.")
                elif result[0] == password:
                    print("Connecté avec succès.")
                    self.erreur.setText("")

                    # Après connexion réussie, afficher la page de visualisation des véhicules
                    vehicules_screen = VehiculesScreen()
                    widget.addWidget(vehicules_screen)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                else:
                    self.erreur.setText("Mot de passe incorrect.")
            except Exception as e:
                self.erreur.setText("Erreur : " + str(e))
            finally:
                conn.close()

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.back_to_home.clicked.connect(self.gotoaccueil)

    def gotoaccueil(self):
        widget.setCurrentIndex(0)

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        lastname = self.nom.text()
        firstname = self.prenom.text()
        birthday = self.birthday.text()

        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0 or len(lastname) == 0 or len(
                firstname) == 0 or len(birthday) == 0:
            self.error.setText("Merci de remplir tous les champs.")

        elif password != confirmpassword:
            self.error.setText("Le mot de passe ne correspond pas.")
        else:
            conn = sqlite3.connect("utilisateurs_data.db")
            cur = conn.cursor()

            user_info = [user, password, lastname, firstname, birthday]
            cur.execute("SELECT Email FROM login_info WHERE Email = ?", (user,))
            if cur.fetchone() is not None:
                self.error.setText("Un compte avec cet email existe déjà.")
            else:
                cur.execute('INSERT INTO login_info (Email, MP, Nom, Prenom, Anniversaire) VALUES (?,?,?,?,?)',
                            user_info)
                conn.commit()
                self.error.setText("Compte créé avec succès.")

                # Après création de compte réussie, afficher la page de visualisation des véhicules
                vehicules_screen = VehiculesScreen()
                widget.addWidget(vehicules_screen)
                widget.setCurrentIndex(widget.currentIndex() + 1)

            conn.commit()
            conn.close()

# Nouvelle classe pour visualiser les véhicules
class VehiculesScreen(QDialog):
    def __init__(self):
        super(VehiculesScreen, self).__init__()
        # Interface simple sans fichier UI
        self.setWindowTitle("Visualisation des Véhicules")
        self.setFixedSize(1200, 800)

        # Création du layout principal
        layout = QVBoxLayout()

        # Titre
        title_label = QLabel("Base de Données des Véhicules")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)

        # Tableau pour afficher les véhicules
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Marque", "Modèle", "Année",
            "Kilométrage", "Prix d'achat", "Coût entretien"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Bouton pour retourner à l'accueil
        button_layout = QHBoxLayout()
        self.back_button = QPushButton("Retour à l'accueil")
        self.back_button.clicked.connect(self.gotoaccueil)
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Initialisation de la base de données et chargement des véhicules
        try:
            self.db = Database("test.db")
            self.parc_controller = ParcController(self.db)

            # Chargement des véhicules
            self.load_vehicules()

            # Si aucun véhicule, générer des exemples
            vehicules = self.parc_controller.rechercher_vehicules()
            if not vehicules or len(vehicules) == 0:
                self.generer_donnees_test()
                self.load_vehicules()

        except Exception as e:
            error_label = QLabel(f"Erreur de connexion à la base de données: {str(e)}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)

    def load_vehicules(self):
        """Charge les véhicules depuis la base de données et les affiche dans le tableau"""
        try:
            # Récupération des véhicules
            vehicules = self.parc_controller.rechercher_vehicules()

            # Configuration du tableau
            self.table.setRowCount(len(vehicules))

            # Remplissage du tableau
            for row, vehicule in enumerate(vehicules):
                # Détermination du type de véhicule
                if isinstance(vehicule, Voiture):
                    type_vehicule = "Voiture"
                elif isinstance(vehicule, Utilitaire):
                    type_vehicule = "Utilitaire"
                elif isinstance(vehicule, Moto):
                    type_vehicule = "Moto"
                else:
                    type_vehicule = "Inconnu"

                # Ajout des données dans le tableau
                self.table.setItem(row, 0, QTableWidgetItem(str(vehicule.id)))
                self.table.setItem(row, 1, QTableWidgetItem(type_vehicule))
                self.table.setItem(row, 2, QTableWidgetItem(vehicule.marque))
                self.table.setItem(row, 3, QTableWidgetItem(vehicule.modele))
                self.table.setItem(row, 4, QTableWidgetItem(str(vehicule.annee)))
                self.table.setItem(row, 5, QTableWidgetItem(f"{vehicule.kilometrage} km"))
                self.table.setItem(row, 6, QTableWidgetItem(f"{vehicule.prix_achat} €"))
                self.table.setItem(row, 7, QTableWidgetItem(f"{vehicule.cout_entretien_annuel} €"))

        except Exception as e:
            print(f"Erreur lors du chargement des véhicules: {str(e)}")

    def generer_donnees_test(self):
        """Génère des exemples de véhicules dans la base de données"""
        try:
            # Ajout de voitures
            self.parc_controller.ajouter_vehicule(
                type_vehicule="Voiture",
                marque="Renault",
                modele="Clio",
                annee=2020,
                kilometrage=15000,
                prix_achat=15000,
                cout_entretien_annuel=800,
                nb_places=5,
                puissance=90,
                carburant="Essence",
                options=["Climatisation", "GPS", "Bluetooth"]
            )

            self.parc_controller.ajouter_vehicule(
                type_vehicule="Voiture",
                marque="Peugeot",
                modele="308",
                annee=2019,
                kilometrage=28000,
                prix_achat=18000,
                cout_entretien_annuel=1000,
                nb_places=5,
                puissance=130,
                carburant="Diesel",
                options=["Climatisation", "GPS", "Caméra de recul"]
            )

            # Ajout d'un utilitaire
            self.parc_controller.ajouter_vehicule(
                type_vehicule="Utilitaire",
                marque="Renault",
                modele="Master",
                annee=2018,
                kilometrage=45000,
                prix_achat=25000,
                cout_entretien_annuel=1500,
                volume=12,
                charge_utile=1200,
                hayon=True
            )

            # Ajout d'une moto
            self.parc_controller.ajouter_vehicule(
                type_vehicule="Moto",
                marque="Honda",
                modele="CB650R",
                annee=2021,
                kilometrage=5000,
                prix_achat=8500,
                cout_entretien_annuel=500,
                cylindree=650,
                type_moto="Roadster"
            )

            print("Données de test générées avec succès!")
        except Exception as e:
            print(f"Erreur lors de la génération des données de test: {str(e)}")

    def gotoaccueil(self):
        """Retourne à l'écran d'accueil"""
        widget.setCurrentIndex(0)


# Code principal
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
    print("Exiting")