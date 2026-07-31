import sys

from PySide6.QtWidgets import QApplication

from ui.facture_dialog import FactureDialog


def main():

    app = QApplication(sys.argv)

    window = FactureDialog()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()