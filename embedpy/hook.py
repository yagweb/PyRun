import os
import sys
import imp
        
def get_files(path):
    if os.path.exists(path):
        return [(bb, os.path.abspath(os.path.join(path, bb))) for bb in os.listdir(path)]
    return []
  
class PyRunLoader:
    def __init__(self, path):
        self.path = path
        
    def load_module(self, fullname):
        return imp.load_dynamic(fullname, self.path)
    
class PyRunFinder:
    def __init__(self, root):
        self.root = root
        module_files = get_files(root)
        self.modules = {}
        for file_name, path in module_files:
            if file_name.endswith(".pyd"):
                module_name = file_name[:-4]
                self.modules[module_name] = path
        
    def find_module(self, fullname, path = None):
        if fullname in sys.modules:
            return sys.modules[fullname]
        if fullname in self.modules: 
            return PyRunLoader(self.modules[fullname])            
        return None        

def register_packages(root):
    packages = [os.path.join(root, "packages"),
                os.path.join(root, "scripts")]
    sys.path.extend(packages)
    
    packages = os.path.join(root, "packages")
    files = get_files(packages)
    for file_name, path in files:
        if file_name.endswith(".zip") or file_name.endswith(".egg"):
            sys.path.append(os.path.abspath(path))            
        
def register():
    root = os.path.abspath(os.path.join(os.__file__, "../../../"))
    register_packages(root)    
    finder = PyRunFinder(os.path.join(root, "extensions"))
    if len(finder.modules) != 0:
        sys.meta_path.append(finder)