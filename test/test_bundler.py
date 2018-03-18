# -*- coding: utf-8 -*-
import os
from pybundle import Bundler

def bundle_core(dirname):    
    bundler = Bundler(dirname)
    bundler.copy_python_dll()
#    unit = bundler.get_unit('python')
#    bundler.add_path("PyRun.py", "test/PyRun2.py", False)
#    bundler.add_path("PyRun.py", "test/PyRun1.py", True)
    bundler.bundle('python', is_compress = True)
    
def bundle_socket(dirname):   
    bundler = Bundler(dirname)
    unit = bundler.create_unit('socket')
    unit.add_dependency('socket')
    unit.bundle(is_compress = True, is_clear = True)
    
    bundler.bundle('python', is_compress = True, is_clear = False)
    
def bundle_sqlite3(dirname):   
    bundler = Bundler(dirname)
    unit = bundler.create_unit('sqlite3')
    unit.add_dependency('sqlite3')
    unit.bundle(is_compress = True, is_clear = True)
    
def bundle_ctypes(dirname):
    bundler = Bundler(dirname)
    unit = bundler.create_unit('ctypes')
    unit.add_dependency('ctypes')
    unit.bundle(is_compress = True, is_clear = True) 
    
def bundle_numpy(dirname):
    bundler = Bundler(dirname)
    unit = bundler.create_unit('numpy')
    unit.add_dependency('numpy')
#    unit.bundle(is_compress = True, is_clear = True)
    unit.bundle(is_compress = False)

def bundle_PyQt5(dirname):
    bundler = Bundler(dirname)
    unit = bundler.create_unit('PyQt5')
    unit.add_dependency('PyQt5')
#    unit.bundle(is_compress = True, is_clear = True)
    unit.bundle(is_compress = False)
    
def bundle_matplotlib():
    bundler = Bundler(dirname)
    unit = bundler.create_unit('matplotlib')
    unit.add_dependency('matplotlib')
#    unit.bundle(is_compress = True, is_clear = True)
    unit.bundle(is_compress = False, is_clear = False)
    
def bundle_pandas():
    bundler = Bundler(dirname)
    unit = bundler.create_unit('pandas')
    unit.add_dependency('pandas')
#    unit.bundle(is_compress = True, is_clear = True)
    unit.bundle(is_compress = False, is_clear = False)
    
def bundle_scipy():
    bundler = Bundler(dirname)
    unit = bundler.create_unit('scipy')
    unit.add_dependency('scipy')
#    unit.bundle(is_compress = True, is_clear = True)
    unit.bundle(is_compress = False, is_clear = False)
    
if __name__ == '__main__':
    dirname = '../bin/'
#    bundle_core(dirname)
#    bundle_socket(dirname)
#    bundle_sqlite3(dirname)
#    bundle_ctypes(dirname)
#    bundle_numpy(dirname)
#    bundle_PyQt5(dirname)
#    bundle_matplotlib()
#    bundle_pandas()
    bundle_scipy()
    