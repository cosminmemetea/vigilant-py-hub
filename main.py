# main.py
import sys
from PyQt5.QtWidgets import QApplication
from analyzer_thread import AnalyzerThread
from ui_components import UIComponents

class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.analyzer = AnalyzerThread()
        self.ui = UIComponents(self.analyzer)  

        self.analyzer.frame_signal.connect(self.ui.update_frame)
        self.analyzer.data_signal.connect(self.ui.update_data)

        self.analyzer.start()
        self.ui.toggle_button.clicked.connect(self.toggle_mode)

        self.ui.showMaximized()

    def toggle_mode(self):
        if self.ui.mode == "Live":
            self.ui.mode = "Static"
            self.ui.toggle_button.setText("Switch to Live")
            self.ui.load_button.setVisible(True)  
            self.analyzer.set_mode("Static")
        else:
            self.ui.mode = "Live"
            self.ui.toggle_button.setText("Switch to Static")
            self.ui.load_button.setVisible(False) 
            self.analyzer.set_mode("Live")

    def closeEvent(self, event):
        self.analyzer.stop()
        event.accept()

if __name__ == "__main__":
    app = MainApp(sys.argv)
    sys.exit(app.exec_())