# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:25:16 2017

libcore bundle at last

@author: yagweb
"""
import os
import pybundle

def bundle_libcore(dirname):
    libcore = pybundle.get_libcore(dirname)
    libcore.bundle()
    
def bundle_ctypes(dirname, zip_file = r'ctypes.zip'):
    libext = pybundle.get_libext(dirname)
    lib = pybundle.bundler(dirname, zip_file)
    pybundle.add_ctypes(lib, libext)
#    lib.bundle() 
    libext.bundle() 
    
def bundle_numpy(dirname):
    libext = pybundle.get_libext(dirname)
#    lib = pybundle.bundler(dirname, r'numpy.zip')
    lib = pybundle.bundler(dirname, None)
    pybundle.add_numpy(lib, libext)
#    lib.bundle()
    libext.bundle() 
    
def bundle_socket(dirname):
    libext = pybundle.get_libext(dirname)
    lib = pybundle.bundler(dirname, r'socket.zip')
    pybundle.add_socket(lib, libext)
    lib.bundle()
    libext.bundle() 
    
def find_python_dll():
    #for windows
    import subprocess
    subprocess.check_call("where python35.dll")

if __name__ == '__main__':
    dirname = '../tmp/'
#    bundle_libcore(dirname)
    dirname = os.path.join(dirname, "packages")
#    bundle_ctypes(dirname)
    bundle_numpy(dirname)