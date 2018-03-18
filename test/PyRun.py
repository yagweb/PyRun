# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 23:54:24 2017

@author: yagweb
"""
import os

def test_socket():
    import socket
    print(socket.__file__)

def test_sqlite3():
    import sqlite3
    print(os.path.abspath("./test.db"))
    cx = sqlite3.connect("./test.db")
    print(cx)

def test_numpy():
    import numpy as np
    print(np.sin(np.arange(10)))
    input()

def test_PyQt5():
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(400, 300)
    w.move(400, 400)
    w.setWindowTitle('hello pyqt5')
    w.show()
    app.exec_()

def test_matplotlib():
    import numpy as np
    import matplotlib.pylab as plt
    
    plt.plot(np.arange(100))
    plt.show()

def test_pandas():
    import pandas as pd
    
    df = pd.DataFrame([[1, 2], [2, 3]])
    print(df)

###############3
#test_socket()
#test_sqlite3()  
#test_numpy()
#test_PyQt5()
#test_matplotlib()
test_pandas()