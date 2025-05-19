import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QStackedWidget
from PyQt5.QtGui import QPalette
import sqlite3


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen,self).__init__()
        loadUi('welcomescreen.ui',self)
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

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen,self).__init__()
        loadUi('login.ui',self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.connexion.clicked.connect(self.loginfunction)

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
                else:
                    self.erreur.setText("Mot de passe incorrect.")
            except Exception as e:
                self.erreur.setText("Erreur : " + str(e))
            finally:
                conn.close()


class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()
        lastname = self.nom.text()
        firstname = self.prenom.text()
        birthday = self.birthday.text()



        if len(user)==0 or len(password)==0 or len(confirmpassword)==0 or len(lastname)==0 or len(firstname)==0 or len(birthday)==0:
            self.error.setText("Merci de remplir tous les champs.")

        elif password!=confirmpassword:
            self.error.setText("Le mot de passe ne correspond pas.")
        else:
            conn = sqlite3.connect("utilisateurs_data.db")
            cur = conn.cursor()

            user_info = [user, password, lastname, firstname, birthday]
            cur.execute('INSERT INTO login_info (Email, MP, Nom, Prenom, Anniversaire) VALUES (?,?,?,?,?)', user_info)

            conn.commit()
            conn.close()




app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget= QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
