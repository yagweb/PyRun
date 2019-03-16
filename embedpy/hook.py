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
    packages = [os.path.join(root, "scripts")]
    sys.path.extend(packages)
    
    packages_dir = os.path.join(root, "packages")
    if packages_dir not in sys.path:
        sys.path.append(packages_dir)
    files = get_files(packages_dir)
    for file_name, path in files:
        if file_name.endswith(".zip") or file_name.endswith(".egg"):
            if file_name == 'python.zip':
                continue
            sys.path.append(os.path.abspath(path))

def hook_multiprocessing():
    '''
    For windows    
    for osx, ref to PyInstaller/loader/rthooks/pyi_rth_multiprocessing.py
    '''
    if sys.platform == 'win32':
        sys.frozen = True
    # must not check the '--multiprocessing-fork' in sys.argv
    # the main process should also set the attr, then the argv passed to subprocess changes
    # from
    # 'xxxx.exe', '-OO', '-S', '-c', 'from multiprocessing.spawn import spawn_main; spawn_main(parent_pid=18652, pipe_handle=884)', '--multiprocessing-fork'
    # to
    # 'xxx.pyc', '--multiprocessing-fork', 'parent_pid=37040', 'pipe_handle=580'
    # then the sub processing can working
        
def register():
    # sys.prefix is the current working memory
    root = os.path.dirname(os.path.realpath(sys.argv[0]))
    register_packages(root)
    finder = PyRunFinder(os.path.join(root, "extensions"))
    if len(finder.modules) != 0:
        sys.meta_path.append(finder)

    hook_multiprocessing()