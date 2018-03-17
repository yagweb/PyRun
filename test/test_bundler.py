# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:25:16 2017

bundle libcore at the last step

@author: yagweb
"""
import os
from pybundle import BundlerCreator

def bundle_core(dirname):
    lib_dir = os.path.join(dirname, "packages")
    pyd_dir = os.path.join(dirname, "extensions")
    dll_dir = os.path.join(dirname, "DLLs")
    creator = BundlerCreator()
    libcore = creator.get_bundler('core')
#    libcore.add_path("PyRun.py", "test/PyRun2.py", False)
#    libcore.add_path("PyRun.py", "test/PyRun1.py", True)
    libcore.bundle(dirname, is_compress = True)
    
def bundle_socket(dirname):
    creator = BundlerCreator()
    libext = creator.create_bundler('socket', 'socket')
    creator.add_module_to_bundler('socket', libext)
    libext.bundle(dirname, is_compress = True)
    
    libcore = creator.get_bundler('core')
    libcore.bundle(dirname, is_compress = True, is_clear = True)
    
def bundle_ctypes(dirname):
    creator = BundlerCreator()
    libext = creator.create_bundler('ctypes', 'ctypes')
    creator.add_module_to_bundler('ctypes', libext)
    libcore = creator.get_bundler('core')
#    libcore.bundle(dirname, is_compress = True) 
#    libcore.bundle(dirname, is_compress = False)
    libext.bundle(dirname, is_compress = True) 
    
def bundle_numpy(dirname):
    creator = BundlerCreator()
    libext = creator.create_bundler('numpy', 'numpy')
    creator.add_module_to_bundler('numpy', libext)
    libext.bundle(dirname, is_compress = True)
    
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