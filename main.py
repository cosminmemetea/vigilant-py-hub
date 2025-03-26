# main.py
import sys
from PyQt5 import QtWidgets, QtCore
from controllers.app_controller import AppController

def main():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    app = QtWidgets.QApplication(sys.argv)
    controller = AppController()
    window = controller.get_main_window()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()