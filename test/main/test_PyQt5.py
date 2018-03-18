import sys
from PyQt5.QtWidgets import QApplication, QWidget

def test_PyQt5():
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(400, 300)
    w.move(400, 400)
    w.setWindowTitle('hello pyqt5')
    w.show()
    app.exec_()
    
test_PyQt5()