# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 13:45:09 2018

@author: yagweb
"""
import os
import sys
import platform
import glob

def get_pyver():
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver

class ModuleDescriptor(object):
    def __init__(self, name):
        self.name = name
        self.modules = []
        self.dependencies = []
        self.paths = []
        self.pyver = get_pyver()
        if sys.platform == "win32":
            self.mod_ext = ".cp%s-win_amd64.pyd" % self.pyver
            self.dll_prefix = ""
            self.dll_ext = ".dll"
        else:
            self.mod_ext = ".cpython-%sm-x86_64-linux-gnu.so" % self.pyver
            self.dll_prefix = "lib"
            self.dll_ext = ".so"
        
    def add_module(self, name, ignore = []):
        self.modules.append([name, ignore])
        
    def add_dependency(self, name):
        self.dependencies.append(name)
        
    def add_dependencies(self, names):
        self.dependencies.extend(names)
        
    def add_path(self, path, dest = None, 
                 is_relative = False, is_glob = False):
        if is_relative:
            path = os.path.join(sys.prefix, path)
        if is_glob:
            paths = glob.glob(path)
            for path in paths:
                if '~' in path:
                    continue
                self.paths.append((path, dest))
        else:
            self.paths.append((path, dest))
    
    def add_dll_in_library_bin(self, name, dest = None):
        path = os.path.join(sys.prefix, 'Library/bin/{0}{1}'.format(name, self.dll_ext))
        self.paths.append((path, dest))
    
    def add_dlls_in_library_bin(self, names, dest = None):
        for name in names:
            path = os.path.join(sys.prefix, 'Library/bin/{0}{1}'.format(name, self.dll_ext))
            self.paths.append((path, dest))
