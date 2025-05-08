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

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen,self).__init__()
        loadUi('login.ui',self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.push2.clicked.connect(self.loginfunction)

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")
        # else:
        #     conn = sqlite3.connect("db_path") # jsp trop comment ça va marcher
        #     cur = conn.cursor()
        #     query = 'SELECT password FROM client WHERE email =\'' + user + "\'"
        #     cur.execute(query)
        #     result_pass = cur.fetchone()[0]
        #     if result_pass == password:
        #         print("Successfully logged in.")
        #         self.error.setText("")
        #     else:
        #         self.error.setText("Invalid username or password")


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
