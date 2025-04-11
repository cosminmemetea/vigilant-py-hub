# main.py
# Entry point for the PyQt5 application, initializes the app and starts the main event loop.

import sys  # Provides access to system-specific parameters and functions, like command-line arguments.
from PyQt5 import QtWidgets, QtCore  # Imports PyQt5 modules for creating the GUI and handling core application features.
from controllers.app_controller import AppController  # Imports the AppController class to manage the application's logic.

def main():
    """Initializes and runs the PyQt5 application."""
    # Enable high-DPI scaling for better display on high-resolution screens.
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # Use high-DPI pixmaps to ensure icons and images scale properly.
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    # Create the PyQt5 application instance, passing command-line arguments.
    app = QtWidgets.QApplication(sys.argv)
    # Instantiate the AppController to handle the application's logic and UI setup.
    controller = AppController()
    # Retrieve the main window from the controller for display.
    window = controller.get_main_window()
    # Show the main window to the user.
    window.show()
    # Start the application's event loop and exit with the app's return code.
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Check if the script is run directly (not imported) and call the main function.
    main()