# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 00:03:50 2018

@author: yagweb
"""
import os
import sys
import platform
from .bundler_unit import ModuleList, BundlerUnit
from .file_utils import copy_file_if_newer

def get_pyver():
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver

class Bundler(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.lib_dir = os.path.join(dirname, "packages")
        self.pyd_dir = os.path.join(dirname, "extensions")
        self.dll_dir = os.path.join(dirname, "DLLs")
        self.descriptors = {}
        self.pyver = get_pyver()
        self.modules = ModuleList()
        
        self.units = {}                     
        
        #register some basic modules
        from .bundler_modules import _platform
        self.register(_platform.get_descriptor())
        from .bundler_modules import _ctypes
        self.register(_ctypes.get_descriptor())
        from .bundler_modules import _socket
        self.register(_socket.get_descriptor())
        from .bundler_modules import _sqlite3
        self.register(_sqlite3.get_descriptor())
        from .bundler_modules import _numpy 
        self.register(_numpy.get_descriptor())
        from .bundler_modules import _PyQt5 
        self.register(_PyQt5.get_descriptor())
        from .bundler_modules import _matplotlib
        self.register(_matplotlib.get_descriptor())
        from .bundler_modules import _pandas
        self.register(_pandas.get_descriptor())
        
        # core bundler, unique
        self.python_unit = self.create_unit('python')
        from .bundler_modules._python import get_descriptor
        des = get_descriptor()
        self.python_unit.add_descriptor(des)
        from .bundler_modules._hook import get_descriptor
        des = get_descriptor()
        self.python_unit.add_descriptor(des)
        
    def copy_python_dll(self):
        if platform.system() == "Windows":
            name = 'python'+self.pyver+'.dll'
            source = os.path.join(sys.prefix, name)
            dest = os.path.join(self.dirname, name)
        else:
            name = 'python'+self.pyver+'.so'
            source = os.path.join(sys.prefix, name)
            dest = os.path.join(self.dirname, name)
        copy_file_if_newer(source, dest)
        
    def register(self, descriptor):
        self.descriptors[descriptor.name] = descriptor
            
    def create_unit(self, name):
        if name in self.units:
            raise Exception('bundler unit %s has exists' % name)
        
        unit = BundlerUnit(name, self,
                              lib_dir = self.lib_dir, 
                              dll_dir = self.dll_dir,
                              pyd_dir = self.pyd_dir)
        self.units[name] = unit
        return unit
        
    def get_unit(self, name):
        unit = self.units.get(name, None)
        if unit is None:
            raise Exception("bundler_unit '%s' not exists" % name)
        return unit
        
    def try_get_descriptor(self, name):
        des = self.descriptors.get(name, None)
        return des
        
    def bundle(self, name, is_compress = True, is_clear = True):
        unit = self.get_unit(name)
        unit.bundle(is_compress = is_compress, 
                    is_clear = is_clear)
        
    def bundle_all(self, is_compress = True, is_clear = True):
        for unit in self.units.values():
            unit.bundle(is_compress = is_compress, 
                        is_clear = is_clear)
