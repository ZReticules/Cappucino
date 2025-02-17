import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QPushButton, QMainWindow, \
    QRadioButton, QComboBox, QSpinBox, QMessageBox

from addEditCoffee import Ui_Dialog
from main_ui import Ui_MainWindow


class AddUpdateForm(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.lastId = 0
        self.con = None
        self.cur = None
        # uic.loadUi('UI/addEditCoffeeForm.ui', self)
        self.setupUi(self)
        self.addButton.clicked.connect(self.addClicked)
        self.delButton.clicked.connect(self.delClicked)
        self.idUpdCombo.currentIndexChanged.connect(self.loadForUpdate)
        self.updButton.clicked.connect(self.updClicked)

    def showEvent(self, a0):
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.cur = self.con.cursor()
        self.updIdCombo()
        # self.cmb = QComboBox(self)
        self.idUpdCombo.setCurrentText(str(self.lastId))
        self.loadForUpdate()

    def updIdCombo(self):
        lastIndex = self.idUpdCombo.currentIndex()
        self.idUpdCombo.currentIndexChanged.disconnect()
        self.idUpdCombo.clear()
        listId = self.cur.execute("""SELECT ID FROM Coffee""").fetchall()
        for i in listId:
            self.idUpdCombo.addItem(str(i[0]))
        self.idUpdCombo.currentIndexChanged.connect(self.loadForUpdate)
        if -1 < lastIndex < self.idUpdCombo.count():
            self.idUpdCombo.setCurrentIndex(lastIndex)

    def loadForUpdate(self):
        # self.rd = QRadioButton(self)
        # self.sb = QSpinBox(self)
        # self.cmb = QComboBox(self)
        self.typeUpdRadio2.setChecked(True)
        result = self.cur.execute(f"""
            SELECT name, degree, type, taste, cost, volume 
            FROM Coffee WHERE ID = {self.idUpdCombo.currentText() or "NULL"}"""
                                  ).fetchall()[0]
        self.nameUpdEdit.setText(result[0])
        self.degreeUpdSpinBox.setValue(result[1])
        self.typeUpdRadio.setChecked(result[2])
        self.tasteUpdEdit.setPlainText(result[3])
        self.costUpdSpinBox.setValue(result[4])
        self.volumeUpdSpinBox.setValue(result[5])

    def addClicked(self):
        self.cur.execute(f"""INSERT INTO COFFEE VALUES(NULL,
            "{self.nameAddEdit.text()}",
            {self.degreeAddSpinBox.text()},
            {"TRUE" if self.typeAddRadio.isChecked() else "FALSE"},
            "{self.tasteAddEdit.toPlainText()}",
            {self.costAddSpinBox.text() or "0"},
            {self.volumeAddSpinBox.text() or "0"}
        )""")
        self.con.commit()
        self.updIdCombo()
        self.loadForUpdate()

    def delClicked(self):
        if QMessageBox.question(
                self, '', f"Действительно удалить элемент с id {self.idUpdCombo.currentText()}",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.cur.execute(f"""DELETE FROM Coffee WHERE ID = {self.idUpdCombo.currentText() or "NULL"}""")
            self.con.commit()
            self.updIdCombo()
            self.loadForUpdate()

    def updClicked(self):
        self.cur.execute(f"""
        UPDATE COFFEE SET
            name = "{self.nameUpdEdit.text()}",
            degree = {self.degreeUpdSpinBox.text()},
            type = {str(self.typeUpdRadio.isChecked()).upper()},
            taste = "{self.tasteUpdEdit.toPlainText()}",
            cost = {self.costUpdSpinBox.text() or "0"},
            volume = {self.volumeUpdSpinBox.text() or "0"}
        WHERE ID = {self.idUpdCombo.currentText() or "NULL"}
        """)
        self.con.commit()
        self.updIdCombo()
        self.loadForUpdate()

    def closeEvent(self, a0):
        self.con.close()


class ViewForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # uic.loadUi('UI/main.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Эспрессо')
        self.showCoffee()
        self.buttonAddUpdate.clicked.connect(self.addUpdate)
        self.buttonRefresh.clicked.connect(self.clickRefresh)
        self.addUpdateForm = AddUpdateForm(self)

    def clickRefresh(self):
        self.showCoffee()

    def addUpdate(self):
        self.addUpdateForm.lastId = int(self.coffeeView.item(self.coffeeView.currentRow(), 0).text())
        self.addUpdateForm.exec()
        self.showCoffee()

    def showCoffee(self):
        con = sqlite3.connect("data/coffee.sqlite")
        cur = con.cursor()
        result = cur.execute(f"""SELECT ID, name, degree, type, taste, cost, volume FROM Coffee""").fetchall()
        con.close()
        self.coffeeView.setColumnCount(7)
        self.coffeeView.setHorizontalHeaderLabels([
            "ID", "Сорт", "Степень прожарки",
            "Молотый/в зернах", "Вкус", "Цена", "Обьем упаковки"
        ])
        self.coffeeView.setRowCount(len(result))
        for i, row in enumerate(result):
            row = list(row)
            row[3] = "Молотый" if row[3] else "В зёрнах"
            row = tuple(row)
            for j, column in enumerate(row):
                self.coffeeView.setItem(i, j, QTableWidgetItem(str(column)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ViewForm()
    ex.show()
    sys.exit(app.exec())
