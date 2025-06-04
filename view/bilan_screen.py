from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from datetime import datetime, timedelta

class BilanScreen(QDialog):
    def __init__(self, parc):
        super().__init__()
        self.parc = parc
        self.setWindowTitle("Bilan comptable annuel")
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()
        self.label_bilan = QLabel()
        self.label_bilan.setStyleSheet("font-size:16px;")
        self.layout.addWidget(self.label_bilan)
        self.setLayout(self.layout)

        self.afficher_bilan()

    def afficher_bilan(self):
        # Données de l'année passée
        aujourd_hui = datetime.now()
        il_y_a_un_an = aujourd_hui - timedelta(days=365)

        chiffre_affaires = 0
        couts_entretien = 0

        for reservation in self.parc.reservations:
            if reservation.statut == "terminée" and reservation.date_fin >= il_y_a_un_an:
                chiffre_affaires += reservation.prix_total

        for vehicule in self.parc.vehicules:
            couts_entretien += vehicule.cout_entretien_annuel

        resultat_net = chiffre_affaires - couts_entretien
        taux_rentabilite = (resultat_net / couts_entretien) * 100 if couts_entretien else 0

        bilan = f"""
💰 **Chiffre d'affaires annuel :** {chiffre_affaires:.2f} €
🛠️ **Coûts d'entretien totaux :** {couts_entretien:.2f} €
📈 **Résultat net :** {resultat_net:.2f} €
📊 **Taux de rentabilité :** {taux_rentabilite:.2f} %
        """
        self.label_bilan.setText(bilan)
