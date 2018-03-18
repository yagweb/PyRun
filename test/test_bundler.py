# -*- coding: utf-8 -*-
import os
from pybundle import Bundler

def bundle_python(dirname):    
    bundler = Bundler(dirname)
    bundler.copy_python_dll()
    bundler.bundle('python', is_compress = True)
    
def bundle_script(dirname, script_path): 
    bundler = Bundler(dirname)
    unit = bundler.create_unit('main')
    unit.add_path(script_path, dest = "../PyRun.py")
    bundler.bundle('main', is_compress = False, is_source = True)
    
def bundle_package(dirname, package_name, main_script = None):
    bundler = Bundler(dirname)
    unit = bundler.create_unit(package_name)
    unit.add_dependency(package_name)
#    unit.bundle(is_compress = True, is_clear = True)
    unit.bundle(is_compress = False, is_clear = False)
    
    if main_script is None:
        main_script = "main/test_" + package_name + ".py"
        
    bundle_script(dirname, main_script)
    
if __name__ == '__main__':
    dirname = '../bin/'
#    bundle_python(dirname)
#    bundle_script(dirname, "main/test_python.py")
#    bundle_package(dirname, 'socket')
#    bundle_package(dirname, 'sqlite3')
#    bundle_package(dirname, 'ctypes')
#    bundle_package(dirname, 'numpy')
#    bundle_package(dirname, 'PyQt5')
#    bundle_package(dirname, 'matplotlib')
#    bundle_package(dirname, 'pandas')
#    bundle_package(dirname, 'scipy')
    bundle_package(dirname, 'traitsui')
    