# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 00:03:50 2018

@author: yagweb
"""
from .bundler import ModuleList, Bundler
from .bundler_modules._python import bundle_python

def get_pyver():
    import platform
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver

class BundlerCreator(object):
    def __init__(self, 
               lib_dir = None, 
               dll_dir = None,
               pyd_dir = None):
        self.lib_dir = lib_dir
        self.dll_dir = dll_dir
        self.pyd_dir = pyd_dir
        self.create_methods = {}
        self.pyver = get_pyver()
        self.modules = ModuleList()
        
        self.bundlers = {}
        
        # core bundler, unique
        self.core_bundler = self.create_bundler('core', 'core')
        bundle_python(self.core_bundler)
        
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
            
    def create_bundler(self, name, dependency_name = None):
        if name in self.bundlers:
            raise Exception('bundler %s has exists' % name)
        
        bundler = Bundler(name, self.modules)
        if dependency_name == name:
            dependency = bundler
        elif dependency_name is None:
            dependency = self.core_bundler
        else:
            dependency = self.bundlers[name][0]
        self.bundlers[name] = (bundler, dependency)
        return bundler
        
    def get_bundler(self, name):
        return self.bundlers[name][0]
 
    def add_module_to_bundler(self, module_name, bundler):
        if isinstance(bundler, str):
            bundler_name = bundler
        else:
            bundler_name = bundler.name
        method = self.create_methods.get(module_name, None)
        if method is None:
            raise Exception("module '%s' not supported" % module_name)
        #add
        bundler, dependency = self.bundlers[bundler_name]
        method(bundler, dependency)
        
    def bundle(self, name):
        bundler = self.get_bundler(name)
        bundler.bundle(is_compress = True, is_clear = True)
        
    def bundle_all(self):
        for bundler in self.bundlers.values():
            bundler.bundle(is_compress = True, is_clear = True)