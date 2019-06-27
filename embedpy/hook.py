import os
import sys
import imp
import time
import datetime
import traceback


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


class MainModuleLoader:
    def __init__(self):
        #sys.argv[0]
        self.program_name = os.path.splitext(os.path.basename(sys.executable))[0]
        self.root = sys.prefix
        self.on_error_from_init = None
        self.on_error_from_main = None
        # self.default_error_file = loader.join("error.txt")
        # under current working directory
        self.default_error_file = os.path.abspath("error.txt")
    
    def initialize(self):
        if os.path.exists(self.default_error_file):
            os.remove(self.default_error_file)
        try:
            self._load()
            return True
        except Exception as ex:
            self.on_error(ex, traceback)
            return False

    def _load(self):
        # load init module
        try:
            self.init_mod = __import__(self.init_mod_name)
        except:
            self.init_mod = None
        
        # get main module name
        if self.init_mod is None:
            self.real_main_mod_name = self.main_mod_name
        else:
            self.real_main_mod_name = self.init_mod.get_main_module(self)
            if hasattr(self.init_mod, "on_error"):
                self.on_error_from_init = self.init_mod.on_error

    def run(self):
        try:
            from runpy import _run_module_as_main
            _run_module_as_main(self.real_main_mod_name, 
                                alter_argv=False)
        except Exception as ex:
            self._init_on_error()
            print('>>>>>>>>')
            print(ex)
            traceback.print_exc()

            # Call the build in error handle
            self.on_error(ex, traceback)

            # Call the user defined on error handle
            is_stop = False
            for on_error in [self.on_error_from_init, 
                             self.on_error_from_main]: 
                if on_error is None:
                    continue
                try:
                    is_stop = on_error(self, ex, traceback)
                    if is_stop:
                        break
                except Exception as inner_ex:
                    self.on_error(inner_ex, traceback)
                    print('>>>>>>>>')
                    print(inner_ex)
                    traceback.print_exc()

    def _init_on_error(self):
        try:
            main_mod = __import__('__main__')
            if hasattr(main_mod, "on_error"):
                self.on_error_from_main = main_mod.on_error
        except:
            pass
    
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

    def on_error(self, ex, tb):
        with open(self.default_error_file, 'w') as fp:
            cur_date = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
            fp.write('--------- Error Log ---------\n\n')
            fp.write(f'Time: {cur_date}\n')
            fp.write('\n--------- Command ---------\n\n')
            fp.write(f"executable: {sys.executable}\n")
            fp.write(f"argv: {sys.argv}\n")
            fp.write('\n--------- Error Info ---------\n\n')
            fp.write(f"{str(ex)}\n")
            fp.write("\n--------- Traceback ----------\n\n")
            # fp.write(traceback.format_exc())
            traceback.print_exc(file=fp)
            fp.write('\n--------- Debug Info ---------\n\n')
            fp.write(f">>> dll search path:\n\n")
            fp.writelines(os.getenv('PATH').strip(";").replace(';;', '\n').replace(';', '\n'))
            fp.write(f"\n\n>>> module search path:\n\n")
            fp.writelines('\n'.join(sys.path))

    def __str__(self):
        return self.root

  
def _register(root):
    '''
    register the pyd modules in extensions folder
    '''
    register_packages(root)
    finder = PyRunFinder(os.path.join(root, "extensions"))
    if len(finder.modules) != 0:
        sys.meta_path.append(finder)


def run():
    sys.prefix = os.path.abspath(os.path.dirname(sys.executable))

    loader = MainModuleLoader()
    _register(loader.root)
    hook_multiprocessing()

    state = loader.initialize()    
    if not state:
        return
    loader.run()
