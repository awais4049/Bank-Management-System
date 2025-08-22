import sys
from PySide6.QtWidgets import QApplication
from library.ui.main_window import MainWindow


def main() -> None:
	app = QApplication(sys.argv)
	app.setApplicationName("Library Manager")
	window = MainWindow()
	window.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()