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
        import platform
        import os
        if platform.system() != 'Windows':
            temp = os.getcwd()
            os.chdir(os.path.dirname(self.path))
            mod = imp.load_dynamic(fullname, self.path) 
            os.chdir(temp)
        else:
            mod = imp.load_dynamic(fullname, self.path)
        return mod
    
class PyRunFinder:
    def __init__(self, root):
        self.root = root
        module_files = get_files(os.path.join(root, "../packages/"))
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

def register_ext_modules(root):
    files = get_files(os.path.join(root, "../packages/"))
    for file_name, path in files:
        if file_name.endswith(".zip"):
            sys.path.append(os.path.abspath(path))            
        
def register(init_path):
    root = os.path.dirname(init_path)    
    register_ext_modules(root)    
    finder = PyRunFinder(root)
    if len(finder.modules) != 0:
        sys.meta_path.append(finder)
