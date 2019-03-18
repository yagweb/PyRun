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


class PathBuilder:
    def __init__(self):
        #sys.argv[0]
        self.program_name = os.path.splitext(os.path.basename(sys.executable))[0]
        self.root = sys.prefix
    
    def join(self, path, is_abs=False):
        if is_abs:
            return os.path.abspath(os.path.join(self.root, path))
        else:
            return os.path.join(self.root, path)

    @property
    def init_mod_name(self):
        return f"__init__{self.program_name}"

    @property
    def main_mod_name(self):
        return f"__main__{self.program_name}"
    
    @property
    def init_mod(self):        
        try:
            init = __import__(self.init_mod_name)
        except:
            init = None
        return init

    def __str__(self):
        return self.root

  
def _register(path):
    '''
    register the pyd modules in extensions folder
    '''
    register_packages(path.root)
    finder = PyRunFinder(path.join("extensions"))
    if len(finder.modules) != 0:
        sys.meta_path.append(finder)


def run():
    sys.prefix = os.path.abspath(os.path.dirname(sys.executable))

    path = PathBuilder()
    _register(path)
    hook_multiprocessing()

    try:
        import traceback
        _run(path)
    except Exception as ex:
        print('>>>>>>>>')
        print(ex)
        traceback.print_exc()
        print('<<<<<<<<')
        mod = path.init_mod
        print(path.init_mod_name, mod)
        if mod is not None:
            try:
                mod.on_err(ex, traceback)
                return
            except Exception as ex:
                print(f'{path.init_mod_name} on_err() exception, {str(ex)}')
        print('Press any key to exit...')
        sys.stdin.read(1)


def _run(path):
    from runpy import _run_module_as_main
    program_name = os.path.basename(sys.argv[0])
    init_name = path.init_mod_name
    try:
        init = __import__(init_name)
    except:
        init = None
    if init is None:
        mod_name = path.main_mod_name
    else:
        mod_name = init.get_main_module(path)
    return _run_module_as_main(mod_name, alter_argv=False)