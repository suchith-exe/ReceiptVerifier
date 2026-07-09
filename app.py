from gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())