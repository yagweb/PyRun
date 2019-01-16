import os
import embedpy
from .bundler import Bundler
from .file_utils import copy_file_if_newer
    
from . import logger

console_path = os.path.join(embedpy.__path__[0], "bases/console.exe")
        
class Freezer(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.bundler = Bundler(dirname, is_freeze=True)
        self.exes = []
        self.python_unit = self.bundler.python_unit
        self.file_unit = self.bundler.create_unit('file_unit', is_compress = False)

    def register(self, descriptors):
        self.bundler.register(descriptors)
        
    def __getitem__(self, name):
        return self.bundler.get_unit(name)
        
    def add_exe(self, script, icon = None, name = None, is_compress = False, is_source = False):
        script_name, ext = os.path.splitext(os.path.basename(script))
        if name is None:
            name = script_name
        self.exes.append((name, script, icon))
        unit = self.bundler.create_unit(f"__main__{name}", is_compress = is_compress, is_source = is_source)
        unit.add_path(script, dest = "../scripts/__main__" + name + ext,
                      is_compile = True, is_override = True)
            
    def create_unit(self, name, is_compress = True, is_source = False):
        return self.bundler.create_unit(name, is_compress = is_compress, 
                                        is_source = is_source)       
            
    def add_path(self, path, dest = None, ignore = ['__pycache__'], 
                 is_compile = None, is_override = False, unit_name = None):
        if unit_name is None:
            unit = self.file_unit
        else:
            unit = self.bundler.get_unit(unit_name)
        unit.add_path(path, dest = dest, ignore = ignore, 
                 is_compile = is_compile, is_override = is_override)
    
    def add_package(self, name, unit_name = None, 
                    is_compress = False, is_source = False,
                    ignore = []):
        if unit_name is None:
            unit_name = name
        if unit_name not in self.bundler.units:
            self.bundler.create_unit(unit_name, is_compress = is_compress, 
                                     is_source = is_source)
        unit = self.bundler.get_unit(unit_name)
        unit.add_dependency(name, ignore = ignore) 
        
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
        for name, script, icon in self.exes:
            exe_path = os.path.join(self.dirname, name + ".exe")
            copy_file_if_newer(console_path, exe_path)       
    