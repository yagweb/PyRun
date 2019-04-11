import os
import sys
import platform
import logging

from .cache import ItemCache, ModuleCache
from .bundler_unit import BundlerUnit
from .file_utils import copy_file_if_newer, mkdir
from .modules import ModuleDescriptor
from .dllcache import DLLCache
from .logger import logger

def get_pyver():
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver

class Bundler(object):
    def __init__(self, dirname, is_freeze=False, logging_level=logging.INFO):
        self.dirname = dirname
        self.setLevel(logging_level)
        self.lib_dir = os.path.join(dirname, "packages")
        self.pyd_dir = os.path.join(dirname, "extensions")
        self.dll_dir = os.path.join(dirname, "DLLs")
        self.descriptors = {}
        self.pyver = get_pyver()
        self.descriptor_cache = ItemCache()
        self.module_cache = ModuleCache()
        self.dll_cache = DLLCache()
        self.dll_cache.add_all_python()
        
        self.units = {}
        
        # register some basic modules
        from .modules import descriptors
        self.register(descriptors)
        
        # core bundler, unique
        # is_compress should not be False
        self.python_unit = self.create_unit('python', is_compress = False)
        self.python_unit.add_dependency('python')
        if is_freeze:
            self.python_unit.add_dependency('hook')
            self.python_unit.add_dependency('runpy')
            self.python_unit.add_dependency('pkgutil')

    def setLevel(self, level):
        logger.setLevel(level)
        
    def __getitem__(self, name):
        return self.get_unit(name)
        
    def copy_python_dll(self):
        mkdir(self.dirname)
        if platform.system() == "Windows":
            name = 'python' + self.pyver + '.dll'
            source = os.path.join(sys.prefix, name)
            dest = os.path.join(self.dirname, name)
        else:
            name = 'python' + self.pyver + '.so'
            source = os.path.join(sys.prefix, name)
            dest = os.path.join(self.dirname, name)
        copy_file_if_newer(source, dest)
        
    def register(self, descriptors):
        if isinstance(descriptors, ModuleDescriptor):
            self.descriptors[descriptors.name] = descriptors
            return
        for des in descriptors:
            if des.name in self.descriptors:
                raise Exception(f"Descriptor '{des.name}' has existed")
            self.descriptors[des.name] = des
            
    def create_unit(self, name, is_compress = False, is_source = False):
        if name in self.units:
            raise Exception('bundler unit %s has exists' % name)

        unit = BundlerUnit(name, self, 
                           is_compress = is_compress, 
                           is_source = is_source,
                           file_dir = self.dirname,
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
        
    def bundle(self, name, is_compress = None, 
               is_source = None, 
               is_clear = False):
        unit = self.get_unit(name)
        unit.bundle(is_compress = is_compress,
                    is_source = is_source)
        
    def bundle_all(self, is_compress = None, 
                   is_source = None):
        for unit in self.units.values():
            unit.bundle(is_compress = is_compress, 
                        is_source = is_source)

    def get_package_dependency(self, name):
        '''
        For debug usage
        It cannot be used for big package, such as numpy
        egg file is not supported.
        '''
        from modulefinder import ModuleFinder
        finder = ModuleFinder()
        mod = __import__(name)
        finder.run_script(mod.__file__)    
        package_names = set()
        for name in finder.modules:
            package_name = name.split('.')[0]
            if package_name not in self.module_cache.modules:
                package_names.add(package_name)
        return package_names

def print_left_dependencies(package_name):
    '''
    a function to help find module dependencies for its descriptor definition.
    Usage:
        Define an empty descriptor
        then call this function, to obtain all the dependencies
        paste all the statement under the descriptor function.
    '''
    bundler = Bundler('')
    unit = bundler.create_unit(package_name)
    unit.add_dependency(package_name)
    buildins = []
    dependencies = []
    for mod in bundler.get_package_dependency(package_name):
        try:
            __import__(mod).__file__
            dependencies.append(mod)
        except:
            buildins.append(mod)
    
    print('buildins: ')
    print(",".join(["'{0}'".format(mod) for mod in buildins]))
    print("--------")
    print('dummy_threading left dependencies, %d:' % len(dependencies))
    for mod in dependencies:
        print("    des.add_dependency('{0}')".format(mod))