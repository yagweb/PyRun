'''
descriptor class
on Windows, we can use dumpbin /DEPENDENTS to find the dependent dlls,
use where to get the path of each dll
'''
import os
import sys
import platform
import glob
import pkg_resources
import multiprocessing
from multiprocessing import Manager


def get_pyver():
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver


def get_modules(name, return_list):
    result = []
    modules = list(sys.modules)
    __import__(name)
    new_modules = list(sys.modules)
    for module_name, module in sys.modules.items():
        if module_name in modules:
            continue
        pack_name = module_name
        while '.' in pack_name:
            pa_name = pack_name.rpartition('.')[0]
            if pa_name not in sys.modules:
                break
            pack_name = pa_name
        if pack_name not in result and \
                hasattr(module, '__file__') and \
                os.path.exists(module.__file__):
            result.append(pack_name)
    return_list.extend(result)


class ModuleDescriptor(object):
    def __init__(self, name):
        self.name = name
        self.modules = {}
        self.dependencies = []
        self.paths = []
        self.dlls = []
        self.dll_search_paths = []
        self.pyver = get_pyver()
        self.python_version = platform.python_version()
        if sys.platform == "win32":
            self.mod_ext = ".cp%s-win_amd64.pyd" % self.pyver
            self.dll_prefix = ""
            self.dll_ext = ".dll"
        else:
            self.mod_ext = ".cpython-%sm-x86_64-linux-gnu.so" % self.pyver
            self.dll_prefix = "lib"
            self.dll_ext = ".so"
        self.is_compressable = True
        
    def add_module(self, name, ignore = [], dest = None, auto_find=False):
        if name == "__main__":
            raise Exception("do not add __main__, use the name explicitly")
        if auto_find:
            self._add_module_with_find(name, ignore=ignore, dest=dest)
        else:
            if name in self.modules:
                return
            self.modules[name] = (name, ignore, dest)

    def _add_module_with_find(self, name, ignore=[], dest=None):
        ''' its impossible to clear all ref by del sys.modules, so we use subprocess here.
        https://stackoverflow.com/questions/6182071/can-i-reliably-unimport-a-python-module-if-i-import-it-in-a-namespace?r=SearchResults
        '''
        manager = Manager()
        return_list = manager.list()
        p = multiprocessing.Process(target=get_modules, args=(name, return_list))
        p.start()
        p.join()
        for item in return_list:
            if item in self.modules:
                return
            self.modules[item] = (item, ignore, dest)
        
    def add_dependency(self, name):
        self.dependencies.append(name)
        
    def add_dependencies(self, names):
        self.dependencies.extend(names)
        
    def add_path(self, path, dest = None, 
                 is_relative = False, is_glob = False, is_compile = None):
        if is_relative:
            path = os.path.join(sys.prefix, path)
        if is_glob:
            paths = glob.glob(path)
            for path in paths:
                if '~' in path:
                    continue
                self.paths.append((path, dest, is_compile))
        else:
            self.paths.append((path, dest, is_compile))
            
    def add_egg_info_files(self, files, module_name = None):
        if module_name is None:
            module_name = self.name
        dist = pkg_resources.get_distribution(module_name)
        if dist.location.endswith('.egg'):
            folder = os.path.join(dist.location, 'EGG-INFO')
        else:
            folder = os.path.join(dist.location, dist.egg_name() + ".egg-info")
        dist_folder = dist.egg_name() + ".egg-info"
        for file in files:
            path = os.path.join(folder, file)
            dest = os.path.join(dist_folder, file)
            self.paths.append((path, dest, True))

    def add_dll(self, name, dest = None):
        if not isinstance(name, str):
            raise Exception(f"dll name should be str")
        self.dlls.append((name, dest))

    def add_dlls(self, names, dest = None):
        for name in names:
            self.add_dll(name, dest)

    def add_dll_search_path(self, path):
        self.dll_search_paths.append(path)