from PySide6.QtWidgets import QApplication

import qdarktheme

import main_window

if __name__ == "__main__":
    app = QApplication()

    qdarktheme.setup_theme()

    window = main_window.MainWindow()
    window.show()

    app.exec()
