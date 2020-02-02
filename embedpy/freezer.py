import os
import logging
import embedpy
from .bundler import Bundler
from .file_utils import copy_file_if_newer
from .logger import logger


console_path = os.path.join(embedpy.__path__[0], "bases/console.exe")
window_path = os.path.join(embedpy.__path__[0], "bases/window.exe")


class Freezer(object):
    def __init__(self, dirname, logging_level=logging.INFO):
        self.dirname = dirname
        self.bundler = Bundler(dirname, logging_level=logging_level)
        self.exes = []
        self.python_unit = self.bundler.create_python_unit(is_freeze=True)
        self.file_unit = self.bundler.create_unit('__file_unit__', is_compress = False)
        self.python_path = []
        self.dll_path = []

    def setLevel(self, level):
        self.bundler.setLevel(level)

    def register(self, descriptors):
        self.bundler.register(descriptors)
        
    def __getitem__(self, name):
        return self.bundler.get_unit(name)

    def add_update_exe(self, name="update", icon=None):
        self.python_unit.add_dependency('update_helper')
        script = os.path.join(os.path.dirname(__file__), "update_main.py")
        self.add_exe(script, icon=icon, name=name)
        
    def add_exe(self, main_script, icon=None, name=None, 
                      is_compress=False, is_source=False,
                      init_script=None,
                      no_console=False,
                      scripts=None):
        if scripts is None:
            scripts = {}
        if name is None:
            name, _ = os.path.splitext(os.path.basename(main_script))
        self.exes.append((name, main_script, icon, no_console))
        unit = self.bundler.create_unit(f"{name}_exe",
                                        is_compress=is_compress,
                                        is_source=is_source)
        scripts["main"] = main_script
        if init_script is not None:
            scripts["init"] = init_script
        # add scripts
        for type_, path in scripts.items():
            _, ext = os.path.splitext(os.path.basename(path))
            unit.add_path(path, 
                          dest=f"../scripts/{name}__{type_}__{ext}",
                          is_compile=True,
                          is_override=True)

    def create_unit(self, name, is_compress=True, is_source=False):
        return self.bundler.create_unit(name, is_compress=is_compress, 
                                        is_source=is_source)
 
    def add_path(self, path, dest=None, ignore=['__pycache__'], 
                 is_compile=None, is_override=False, unit_name=None):
        if unit_name is None:
            unit = self.file_unit
        else:
            unit = self.bundler.get_unit(unit_name)
        unit.add_path(path, dest=dest, ignore=ignore, 
                 is_compile=is_compile, is_override=is_override)

    def add_dll(self, name, dest=None, unit_name=None):
        if unit_name is None:
            unit = self.file_unit
        else:
            unit = self.bundler.get_unit(unit_name)
        unit.add_dll(name, dest=dest)
    
    def add_package(self, name, unit_name=None, 
                    is_compress=False, is_source=False,
                    ignore=None):
        if ignore is None:
            ignore = []
        if unit_name is None:
            unit_name = name
        if unit_name not in self.bundler.units:
            self.bundler.create_unit(unit_name, is_compress=is_compress, 
                                     is_source=is_source)
        unit = self.bundler.get_unit(unit_name)
        unit.add_dependency(name, ignore=ignore)

    def add_python_path(self, path):
        self.python_path.append(path)

    def add_dll_path(self, path):
        self.dll_path.append(path)
        
    def build(self):
        if not os.path.exists(self.dirname):
            logger.info('create folder %s' % os.path.abspath(self.dirname))
            pa = os.path.dirname(self.dirname)
            if not os.path.exists(pa):
                os.mkdir(pa)
            os.mkdir(self.dirname)
        
        logger.info('copying python dll')
    #    bundler.python_unit.clear_package()
        self.bundler.copy_python_dll()
        
        logger.info('bundling packages')
        self.bundler.bundle_all(is_compress = None, is_source = None)
        
        logger.info('copying exes')
        for name, script, icon, no_console in self.exes:
            exe_path = os.path.join(self.dirname, name + ".exe")
            if no_console:
                copy_file_if_newer(window_path, exe_path)
            else:
                copy_file_if_newer(console_path, exe_path)

        if self.python_path:
            logger.info('generate python path')
            with open(os.path.join(self.dirname, ".pth"), 'w') as fp:
                fp.write("\n".join(self.python_path))

        if self.dll_path:
            logger.info('generate python path')
            with open(os.path.join(self.dirname, "PATH"), 'w') as fp:
                fp.write("\n".join(self.dll_path))