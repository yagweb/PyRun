# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 10:15:37 2018

@author: yagweb
"""
import sys
from embedpy.freezer import Freezer

def freeze_test(dest_path): 
    sys.argv.append('build')
    print('build start.')
    fr = Freezer(dest_path)
    fr.add_package('ctypes')
    fr.add_exe("main/test_ctypes.py", name = "test")
    fr.build()
    print('build end.')    
    
if __name__ == '__main__':
    dest_path = r'..\bin\demo'
    freeze_test(dest_path)
