import os
import sqlite3

def test_sqlite3():    
    print(os.path.abspath("./test.db"))
    cx = sqlite3.connect("./test.db")
    print(cx)
    
test_sqlite3()