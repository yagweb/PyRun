# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 00:03:50 2018

@author: yagweb
"""
import os
from .bundler_unit import ModuleList, BundlerUnit
from .bundler_modules._python import bundle_python

def get_pyver():
    import platform
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver

class Bundler(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.lib_dir = os.path.join(dirname, "packages")
        self.pyd_dir = os.path.join(dirname, "extensions")
        self.dll_dir = os.path.join(dirname, "DLLs")
        self.create_methods = {}
        self.pyver = get_pyver()
        self.modules = ModuleList()
        
        self.units = {}
        
        # core bundler, unique
        self.core_unit = self.create_unit('core', 'core')
        bundle_python(self.core_unit)
        
        #register some basic modules
        from .bundler_modules import _ctypes
        self.register_module(_ctypes)
        from .bundler_modules import _socket
        self.register_module(_socket)
        from .bundler_modules import _numpy 
        self.register_module(_numpy)
        
    def register_module(self, module):        
        module_name, method = module.get_method(self.pyver)
        if method is None:
            raise Exception('%s is not supported for python %s' % (module_name, self.pyver))
        self.create_methods[module_name] = method
            
    def create_unit(self, name, dependency_name = None):
        if name in self.units:
            raise Exception('bundler %s has exists' % name)
        
        bundler = BundlerUnit(name, self.modules,
                              lib_dir = self.lib_dir, 
                              dll_dir = self.dll_dir,
                              pyd_dir = self.pyd_dir)
        if dependency_name == name:
            dependency = bundler
        elif dependency_name is None:
            dependency = self.core_unit
        else:
            dependency = self.units[name][0]
        self.units[name] = (bundler, dependency)
        return bundler
        
    def get_unit(self, name):
        return self.units[name][0]
 
    def add_module_to_unit(self, module_name, bundler):
        if isinstance(bundler, str):
            bundler_name = bundler
        else:
            bundler_name = bundler.name
        method = self.create_methods.get(module_name, None)
        if method is None:
            raise Exception("module '%s' not supported" % module_name)
        #add
        bundler, dependency = self.units[bundler_name]
        method(bundler, dependency)
        
    def bundle(self, name, is_compress = True, is_clear = True):
        unit = self.get_unit(name)
        unit.bundle(is_compress = is_compress, 
                    is_clear = is_clear)
        
    def bundle_all(self, is_compress = True, is_clear = True):
        for unit in self.units.values():
            unit.bundle(is_compress = is_compress, 
                        is_clear = is_clear)
