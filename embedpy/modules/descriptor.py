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
        
    def add_module(self, name, ignore = [], dest = None):
        if name == "__main__":
            raise Exception("do not add __main__, use the name explicitly")
        self.modules.append([name, ignore, dest])
        
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

    def add_dll_in_root(self, name, dest = None):
        path = os.path.join(sys.prefix, '{0}{1}'.format(name, self.dll_ext))
        self.paths.append((path, dest, None))

    def add_dll_in_DLLs(self, name, dest = None):
        path = os.path.join(sys.prefix, 'DLLs/{0}{1}'.format(name, self.dll_ext))
        self.paths.append((path, dest, None))
    
    def add_dll_in_library_bin(self, name, dest = None):
        path = os.path.join(sys.prefix, 'Library/bin/{0}{1}'.format(name, self.dll_ext))
        self.paths.append((path, dest, None))
    
    def add_dlls_in_library_bin(self, names, dest = None):
        for name in names:
            path = os.path.join(sys.prefix, 'Library/bin/{0}{1}'.format(name, self.dll_ext))
            self.paths.append((path, dest, None))