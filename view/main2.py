import sys
import sqlite3

from enum import IntEnum
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QDialog, QStackedWidget,
    QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QHeaderView
)
from PyQt5.QtCore import Qt

from utils.database import Database
from controller.parc_controller import ParcController
from model.vehicule import Voiture, Utilitaire, Moto
from reservation_screen import ReservationScreen
from utils.password import hash_password_bcrypt, verify_password_bcrypt

from screens import Screen

# Votre enum, vous pouvez bien sûr l'extraire dans un module séparé

class WelcomeScreen(QDialog):
    def __init__(self):
        super().__init__()
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

        self.push.clicked.connect(self.goToLogin)
        self.push2.clicked.connect(self.goToCreateAccount)
        self.pushButton_3.clicked.connect(self.goToAdmin)

    def goToLogin(self):
        widget.setCurrentIndex(Screen.LOGIN)

    def goToCreateAccount(self):
        widget.setCurrentIndex(Screen.CREATE_ACCOUNT)

    def goToAdmin(self):
        widget.setCurrentIndex(Screen.ADMIN)


class LoginScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('login.ui', self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.connexion.clicked.connect(self.loginfunction)
        self.back_to_home.clicked.connect(self.goToWelcome)

    def goToWelcome(self):
        widget.setCurrentIndex(Screen.WELCOME)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if not user or not password:
            self.erreur.setText("Merci de remplir tous les champs.")
            return

        conn = sqlite3.connect("utilisateurs_data.db")
        cur = conn.cursor()
        try:
            cur.execute("SELECT MP FROM login_info WHERE Email = ?", (user,))
            result = cur.fetchone()
            if result is None:
                self.erreur.setText("Cet identifiant n'existe pas.")
            elif verify_password_bcrypt(result[0], password):
                self.erreur.setText("")
                widget.setCurrentIndex(Screen.RESERVATION)
            else:
                self.erreur.setText("Mot de passe incorrect.")
        except Exception as e:
            self.erreur.setText("Erreur : " + str(e))
        finally:
            conn.close()


class AdminScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('admiN.ui', self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.connexion.clicked.connect(self.loginfunction)
        self.back_to_home.clicked.connect(self.goToWelcome)

    def goToWelcome(self):
        widget.setCurrentIndex(Screen.WELCOME)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if not user or not password:
            self.erreur.setText("Merci de remplir tous les champs.")
            return

        conn = sqlite3.connect("gestionnaires_data.db")
        cur = conn.cursor()
        try:
            cur.execute("SELECT MP FROM GESTIONNAIRES WHERE Email = ?", (user,))
            result = cur.fetchone()
            if result is None:
                self.erreur.setText("Cet identifiant n'existe pas.")
            elif result[0] == password:
                self.erreur.setText("")
                widget.setCurrentIndex(Screen.VEHICULES)
            else:
                self.erreur.setText("Mot de passe incorrect.")
        except Exception as e:
            self.erreur.setText("Erreur : " + str(e))
        finally:
            conn.close()


class CreateAccScreen(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("createacc.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.back_to_home.clicked.connect(self.goToWelcome)

    def goToWelcome(self):
        widget.setCurrentIndex(Screen.WELCOME)

    def signupfunction(self):
        user        = self.emailfield.text()
        password    = self.passwordfield.text()
        confirm     = self.confirmpasswordfield.text()
        lastname    = self.nom.text()
        firstname   = self.prenom.text()
        birthday    = self.birthday.text()

        if not all([user, password, confirm, lastname, firstname, birthday]):
            self.error.setText("Merci de remplir tous les champs.")
            return

        if password != confirm:
            self.error.setText("Le mot de passe ne correspond pas.")
            return

        conn = sqlite3.connect("utilisateurs_data.db")
        cur = conn.cursor()
        try:
            cur.execute("SELECT Email FROM login_info WHERE Email = ?", (user,))
            if cur.fetchone():
                self.error.setText("Un compte avec cet email existe déjà.")
            else:
                passwordHash = hash_password_bcrypt(password)
                cur.execute(
                    'INSERT INTO login_info (Email, MP, Nom, Prenom, Anniversaire) VALUES (?,?,?,?,?)',
                    (user, passwordHash, lastname, firstname, birthday)
                )
                conn.commit()
                self.error.setText("Compte créé avec succès.")
                widget.setCurrentIndex(Screen.RESERVATION)
        except Exception as e:
            self.error.setText("Erreur : " + str(e))
        finally:
            conn.close()


class VehiculesScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualisation des Véhicules")
        self.setFixedSize(1200, 800)

        layout = QVBoxLayout()
        title = QLabel("Base de Données des Véhicules")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px;font-weight:bold;margin:20px;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Marque", "Modèle", "Année",
            "Kilométrage", "Prix d'achat", "Coût entretien"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        back = QPushButton("Retour à l'accueil")
        back.clicked.connect(self.goToWelcome)

        btn_layout.addStretch()
        btn_layout.addWidget(back)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        # (chargement BD identique à avant…)

    def goToWelcome(self):
        widget.setCurrentIndex(Screen.WELCOME)



# --- Code principal ---
app = QApplication(sys.argv)
widget = QStackedWidget()
widget.setFixedSize(1200, 800)

# Instanciation de tous les écrans dans l’ordre défini par Screen
screens = [
    WelcomeScreen(),
    LoginScreen(),
    CreateAccScreen(),
    AdminScreen(),
    VehiculesScreen(),
    ReservationScreen()
]
for screen in screens:
    widget.addWidget(screen)

widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")

