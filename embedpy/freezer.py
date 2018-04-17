import os
import embedpy
from .bundler import Bundler
from .file_utils import copy_file_if_newer

console_path = os.path.join(embedpy.__path__[0], "bases/console.exe")
        
class Freezer(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.bundler = Bundler(dirname)
        self.exe_bundler = Bundler(dirname)
        self.exes = []
        
    def add_exe(self, script, icon = None, name = None):
        script_name, ext = os.path.splitext(os.path.basename(script))
        if name is None:
            name = script_name
        self.exes.append((name, script, icon))
        unit = self.exe_bundler.create_unit(name)
        unit.add_path(script, dest = "../scripts/script_" + name + ext,
                      is_compile = True, is_override = True)
            
    def create_unit(self, name):
        return self.bundler.create_unit(name)
    
    def add_package(self, name, unit_name = None):
        if unit_name is None:
            unit_name = name
        if unit_name not in self.bundler.units:
            self.bundler.create_unit(unit_name)
        unit = self.bundler.get_unit(unit_name)
        unit.add_dependency(name)
        
    def build(self):
        if not os.path.exists(self.dirname):
            print('create folder %s' % os.path.abspath(self.dirname))
            os.mkdir(self.dirname)
        
        print('copying python dll')
    #    bundler.python_unit.clear_package()
        self.bundler.bundle('python', is_compress = True)
        self.bundler.copy_python_dll()
        
        print('copying exes')
        for name, script, icon in self.exes:
            exe_path = os.path.join(self.dirname, name + ".exe")
            copy_file_if_newer(console_path, exe_path)
        
        print('bundling packages')
        self.exe_bundler.bundle_all(is_compress = False, is_source = True) 
        self.bundler.bundle_all(is_compress = False, is_source = True)       
    