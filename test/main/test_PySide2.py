import sys
from PySide2.QtWidgets import QApplication, QWidget

def test_PySide2():
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(400, 300)
    w.move(400, 400)
    w.setWindowTitle('hello pyqt5')
    w.show()
    app.exec_()
    
test_PySide2()