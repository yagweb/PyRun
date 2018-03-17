# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 10:15:37 2018

@author: yagweb
"""
import sys
from pybundle.freezer import Freezer

def freeze_test(dest_path): 
    sys.argv.append('build')
    print('build start.')
    fr = Freezer()
    fr.add_numpy()
    fr.add_matplotlib()
    fr.add_traitsui()
    fr.add_package('packaging')
    fr.add_package('socket')
    fr.add_package('scipy')
    fr.add_package('sqlalchemy')
    fr.add_package('sqlalchemy.ext.declarative')
    fr.build("PyRun", dest_path)
#    shutil.copy("PyRun.py", os.path.join(dest_path, "PyRun.py"))
    print('build end.')    
    
if __name__ == '__main__':
    dest_path = r'..\bin\PyRun'
    freeze_test(dest_path)
