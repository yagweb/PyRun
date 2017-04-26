# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 00:34:58 2017

@author: yagweb
"""
import os
import sys
try:    
    __import__(os.path.splitext(os.path.basename(sys.argv[0]))[0])
except Exception as ex:
    print(">>>>>>>>>>>>>")    
    print(ex) 
    print("<<<<<<<<<<<<<")      
    input('press Enter key to exit')