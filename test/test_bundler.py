# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:25:16 2017

bundle libcore at the last step

@author: yagweb
"""
import os
from pybundle import Bundler

def bundle_core(dirname):    
    bundler = Bundler(dirname)
#    unit = bundler.get_unit('python')
#    bundler.add_path("PyRun.py", "test/PyRun2.py", False)
#    bundler.add_path("PyRun.py", "test/PyRun1.py", True)
    bundler.bundle('python', is_compress = True)
    
def bundle_socket(dirname):   
    bundler = Bundler(dirname)
    libext = bundler.create_unit('socket', 'socket')
    bundler.add_module_to_unit('socket', libext)
    libext.bundle(is_compress = True, is_clear = True)
    
    bundler.bundle('python', is_compress = True, is_clear = False)
    
def bundle_sqlite3(dirname):   
    bundler = Bundler(dirname)
    libext = bundler.create_unit('sqlite3', 'sqlite3')
    bundler.add_module_to_unit('sqlite3', libext)
    libext.bundle(is_compress = True, is_clear = True)
    
def bundle_ctypes(dirname):
    bundler = Bundler(dirname)
    libext = bundler.create_unit('ctypes', 'ctypes')
    bundler.add_module_to_unit('ctypes', libext)
    libext.bundle(is_compress = True, is_clear = True) 
    
def bundle_numpy(dirname):
    bundler = Bundler(dirname)
    bundler.copy_python_dll()
    import pdb
    pdb.set_trace()
    libext = bundler.create_unit('numpy', 'numpy')
    bundler.add_module_to_unit('numpy', libext)
#    libext.bundle(is_compress = True, is_clear = True)
    libext.bundle(is_compress = False)
    
def find_python_dll():
    #for windows
    import subprocess
    subprocess.check_call("where python36.dll")
    
if __name__ == '__main__':
    dirname = '../bin/'
    bundle_core(dirname)
#    bundle_socket(dirname)
#    bundle_sqlite3(dirname)
#    bundle_ctypes(dirname)
#    bundle_numpy(dirname)
    