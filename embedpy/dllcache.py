import os
import sys
from .file_utils import file_util


class DLLCache:
    def __init__(self):
        self.dlls = {}
        self.env_paths = os.environ["PATH"].split(";")

    def add_rel_path(self, path):
        path = os.path.join(sys.prefix, path)
        self.add_path(path)

    def add_path(self, path):
        print(f"add dll path: {path}")
        if not os.path.isdir(path):
            return
        for file in os.listdir(path):
            if not file.endswith(file_util.dll_ext):
                continue
            abs_path = os.path.join(path, file)
            dll_name = file.split('.')[0]
            if dll_name in self.dlls:
                print(f"warning: {dll_name} has added")
                continue
            self.dlls[dll_name] = abs_path
    
    def add_all(self):
        for path in self.env_paths:
            self.add_path(path)

    def add_all_python(self):
        cur = sys.prefix.replace("\\", "/").strip("/")
        for path in self.env_paths:
            path = path.replace("\\", "/")
            if path.startswith(cur):
                self.add_path(path)
    
    def get(self, name):
        return self.dlls.get(name)
