import os
import sys
import platform
import logging
import shutil
import zipfile

from .cache import ItemCache, ModuleCache
from .bundler_unit import BundlerUnit
from .file_utils import copy_file_if_newer, mkdir
from .modules import ModuleDescriptor
from .dllcache import DLLCache
from .logger import logger_helper, logger


def get_pyver():
    temp = platform.python_version().split('.')
    pyver = "%s%s" % (temp[0], temp[1])
    return pyver


class Bundler(object):
    def __init__(self, dirname, logging_level=logging.INFO):
        self.dirname = dirname
        self.setLevel(logging_level)
        self.lib_dir = os.path.join(dirname, "packages")
        self.pyd_dir = os.path.join(dirname, "extensions")
        self.dll_dir = os.path.join(dirname, "DLLs")
        self.descriptors = {}
        self.platform = sys.platform
        self.pyver = get_pyver()
        self.descriptor_cache = ItemCache()
        self.module_cache = ModuleCache()
        self.dll_cache = DLLCache()
        self.dll_cache.add_all_python()
        
        self.units = {}
        
        # register some basic modules
        from .modules import descriptors
        self.register(descriptors)

    def add_dll_search_path(self, path):
        self.dll_cache.add_path(path)

    def create_python_unit(self, is_compress=False, is_freeze=False, name="python"):
        # core bundler, unique
        # is_compress should not be False
        python_unit = self.create_unit(name, is_compress=is_compress)
        python_unit.add_dependency('python')
        if is_freeze:
            python_unit.add_dependency('hook')
            python_unit.add_dependency('runpy')
            python_unit.add_dependency('pkgutil')
            python_unit.add_dependency('datetime')
        return python_unit

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

    def create_unit(self, name, is_compress=False, is_source=False):
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

    def _bundle_all(self, is_compress=None, 
                   is_source=None):
        dll_missing = []
        for unit in self.units.values():
            unit._bundle(is_compress = is_compress, 
                        is_source = is_source)
            dll_missing.extend(unit.dll_missing)
        return dll_missing

    def bundle_all(self, is_compress=None, 
                   is_source=None):
        from io import StringIO
        stream = StringIO()
        logger_helper.add_stream_handler(name="err", stream=stream, 
                            fstr=None, level=logging.ERROR)
        dll_missing = self._bundle_all(is_compress=is_compress, is_source=is_source)
        print("-------------------Errors-------------------")
        print(stream.getvalue())
        if dll_missing:
            logger.error(f"dlls {','.join(dll_missing)} not found")
            logger.error(f"dll search paths: \n{self.dll_cache.search_path}")
        logger_helper.remove_handler("err")

    def build_zipfile(self, file_name):
        print(f'build zipfile {file_name} ...')
        if os.path.exists(file_name):
            os.remove(file_name)
        root = os.path.dirname(self.dirname)
        with zipfile.ZipFile(file_name, 'w') as target:
            target.write(self.dirname, os.path.basename(self.dirname))
            for cur_root, cur_dirs, cur_files in os.walk(self.dirname):
                for dir in cur_dirs:
                    full_path = os.path.join(cur_root, dir)
                    rel_path = os.path.relpath(full_path, root)
                    target.write(full_path, rel_path)
                for file in cur_files:
                    full_path = os.path.join(cur_root, file)
                    rel_path = os.path.relpath(full_path, root)
                    target.write(full_path, rel_path)

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


class UpdateBundler(Bundler):
    def __init__(self, dirname, logging_level=logging.INFO):
        dirname = os.path.join(dirname, "update")
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        super(UpdateBundler, self).__init__(dirname, logging_level=logging_level)
        self.file_unit = self.create_unit('__file_unit__', is_compress = False)

    def create_unit_by_package(self, package, is_compress=False, is_source=False):
        unit = self.create_unit(package, 
                                is_compress=is_compress,
                                is_source = is_source)
        unit.add_package(package)
        unit.clear_package()
        return unit
 
    def add_path(self, path, dest=None, ignore=['__pycache__'], 
                 is_compile=None, is_override=False, unit_name=None):
        if unit_name is None:
            unit = self.file_unit
        else:
            unit = self.get_unit(unit_name)
        unit.add_path(path, dest=dest, ignore=ignore, 
                 is_compile=is_compile, is_override=is_override)

    def build_update_zipfile(self, version=None):
        if version:
            version = f"-{version}"
        else:
            version =""
        file_name = os.path.join(self.dirname, f"../update{version}.zip")
        self.build_zipfile(file_name)


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
