import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWheelEvent
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QTime


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setFixedSize(500, 500)
        self.setWindowTitle("La DOS Roulette")
        self.setCentralWidget(MainWidget())


class MainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.mainLabel = QLabel("<h1>Time : 0 ms | Ticks : 0</h1>")
        self.scrollCounter = ScrollCounter()
        self.scrollCounter.start()
        self.scrollZone = ScrollZone()
        vbox = QVBoxLayout()
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.scrollZone, 1)
        self.setLayout(vbox)
        self.scrollZone.scrollDownSignal.connect(self.scrollCounter.scrollEvent)
        self.scrollCounter.scrollMeasureSignal.connect(self.scrollMeasureEvent)

    def scrollMeasureEvent(self, timeMs, tickCounter):
        self.mainLabel.setText("<h1>Time : {} ms | Ticks : {}</h1>".format(timeMs, tickCounter))

    def __del__(self):
        self.scrollCounter.stop()
        self.scrollCounter.wait()


class ScrollCounter(QThread):
    scrollMeasureSignal = pyqtSignal(int, int)
    scrollStartSignal = pyqtSignal()
    scrollStopSignal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.running = False
        self.scrollingTimer = QTimer()
        self.scrollingTimer.setSingleShot(True)
        self.scrollingTimer.timeout.connect(self.scrollEventStop)
        self.time = QTime()
        self.counter = 0

    def run(self):
        self.running = True
        while self.running:
            QThread.usleep(100)
            if self.scrollingTimer.isActive():
                self.scrollMeasureSignal.emit(self.time.elapsed(), self.counter)
        self.running = False

    def stop(self):
        self.running = False

    def scrollEvent(self):
        if not self.scrollingTimer.isActive():
            self.counter = 1
            self.time.start()
            self.scrollStartSignal.emit()
        else:
            self.counter += 1
        self.scrollingTimer.start(200)

    def scrollEventStop(self):
        self.scrollMeasureSignal.emit(self.time.elapsed(), self.counter)
        self.counter = 0
        self.scrollStopSignal.emit()


class ScrollZone(QLabel):
    scrollDownSignal = pyqtSignal()

    def __init__(self):
        QLabel.__init__(self)
        self.setStyleSheet("""
        QFrame, QLabel, QToolTip {
            border: 2px solid green;
            border-radius: 4px;
        }
        """)
        self.setMouseTracking(True)

    def wheelEvent(self, *args, **kwargs):
        QLabel.wheelEvent(self, *args, **kwargs)
        if len(args) == 1 and isinstance(args[0], QWheelEvent):
            wevent = args[0]
            if wevent.delta() < 0:
                # Scroll down
                self.scrollDownSignal.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
