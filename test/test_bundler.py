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
#    unit = bundler.get_unit('core')
#    bundler.add_path("PyRun.py", "test/PyRun2.py", False)
#    bundler.add_path("PyRun.py", "test/PyRun1.py", True)
    bundler.bundle('core', is_compress = True)
    
def bundle_socket(dirname):   
    bundler = Bundler(dirname)
    libext = bundler.create_unit('socket', 'socket')
    bundler.add_module_to_unit('socket', libext)
    libext.bundle(is_compress = True, is_clear = True)
    
    bundler.bundle('core', is_compress = True, is_clear = False)
    
def bundle_ctypes(dirname):
    bundler = Bundler(dirname)
    libext = bundler.create_unit('ctypes', 'ctypes')
    bundler.add_module_to_unit('ctypes', libext)
    libext.bundle(is_compress = True, is_clear = True) 
    
def bundle_numpy(dirname):
    bundler = Bundler(dirname)
    libext = bundler.create_unit('numpy', 'numpy')
    bundler.add_module_to_unit('numpy', libext)
#    libext.bundle(is_compress = True, is_clear = True)
    libext.bundle(is_compress = False)
    
def find_python_dll():
    #for windows
    import subprocess
    subprocess.check_call("where python35.dll")
    
if __name__ == '__main__':
    dirname = '../bin/'
#    bundle_core(dirname)
#    bundle_socket(dirname)
#    bundle_ctypes(dirname)
    bundle_numpy(dirname)
    