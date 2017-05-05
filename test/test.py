# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:25:16 2017

libcore bundle at last

@author: yagweb
"""
import os
import pybundle

def bundle_libcore(dirname):
    libcore = pybundle.get_libcore()
#    libcore.add_path("PyRun.py", "test/PyRun2.py", False)
#    libcore.add_path("PyRun.py", "test/PyRun1.py", True)
    libcore.bundle(dirname, zip_file= 'libcore.zip')
    
def bundle_ctypes(dirname, zip_file = r'ctypes.zip'):
    libext = pybundle.get_libext()
    lib = pybundle.bundler()
    pybundle.add_ctypes(lib, libext)
#    lib.bundle(dirname, zip_file) 
    lib.bundle(dirname, None) 
    libext.bundle(dirname, libext.zip_file) 
    
def bundle_numpy(dirname, zip_file = r'numpy.zip'):
    libext = pybundle.get_libext()
    lib = pybundle.bundler()
    pybundle.add_numpy(lib, libext)
#    lib.bundle(dirname, zip_file) 
    lib.bundle(dirname, None) 
    libext.bundle(dirname, libext.zip_file) 
    
def bundle_socket(dirname, zip_file = r'socket.zip'):
    libext = pybundle.get_libext()
    lib = pybundle.bundler()
    pybundle.add_socket(lib, libext)
#    lib.bundle(dirname, zip_file) 
    libext.bundle(dirname, libext.zip_file) 
    
def find_python_dll():
    #for windows
    import subprocess
    subprocess.check_call("where python35.dll")

def freeze_test(): 
    import sys
    import shutil
    from pybundle import freezer
    sys.argv.append('build')
    print('build start.')
    dest_path = r'..\bin\PyRun'
    fr = freezer()
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
    dirname = '../bin/'
#    bundle_libcore(dirname)
#    dirname = os.path.join(dirname, "packages")
#    bundle_ctypes(dirname)
#    bundle_numpy(dirname)
#    bundle_socket(dirname)
    freeze_test()