# main.py
import sys
from PyQt5.QtWidgets import QApplication
from video_stream import VideoStream
from ui_components import UIComponents

class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.ui = UIComponents()
        self.video_stream = VideoStream()

        # Connect signals
        self.video_stream.frame_signal.connect(self.ui.update_frame)
        self.video_stream.data_signal.connect(self.ui.update_data)

        self.video_stream.start()
        self.ui.showMaximized()

    def closeEvent(self, event):
        self.video_stream.stop()
        event.accept()

if __name__ == "__main__":
    app = MainApp(sys.argv)
    sys.exit(app.exec_())