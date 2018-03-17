# -*- coding: utf-8 -*-
"""
@author: YangWenguang
Issues contact with: hbtmdxywg@126.com
"""
import os
import shutil

python_source_lib = os.path.abspath(os.path.dirname(os.__file__))
    
def copy_file_if_newer(src, dest):
    if not os.path.exists(src):
        raise Exception("%s not exist" % dest)
    if not os.path.exists(dest) or \
       os.stat(src).st_mtime > os.stat(dest).st_mtime:
        shutil.copy(src, dest)
        print("%s update." % dest)
        return
    print("%s reused." % dest) 

def is_file_out_of_date(file, references):
    if os.path.exists(file):
        for source in references:
            if os.stat(source).st_mtime > os.stat(file).st_mtime:
                return True
                break 
    return False
            
def remove_file_if_out_of_date(file, references):
    if is_file_out_of_date(file, references):
        print("file '%s' is out of date" % file)
        os.remove(file)

class FileUtil(object):
    def  __init__(self):
        import platform
        temp = platform.python_version().split('.')
        pyver = "%s%s" % (temp[0], temp[1])
        if platform.system() == "Windows":
            self.mod_ext = ".cp%s-win_amd64.pyd" % pyver
            self.dll_prefix = ""
            self.dll_ext = ".dll"
        else:
            self.mod_ext = ".cpython-%sm-x86_64-linux-gnu.so" % pyver
            self.dll_prefix = "lib"
            self.dll_ext = ".so"
            
    def get_mod_name(self, mod_file):
        file_name = os.path.basename(mod_file)
        return file_name[:len(file_name)-len(self.mod_ext)]
            
    def get_mod_file(self, mod_name):
        return mod_name + self.mod_ext
    
    def get_mod_files(self, mod_names):
        return [mod_name + self.mod_ext for mod_name in mod_names]
            
    def get_dll_file(self, dll):
        temp = dll.replace("\\", "/").split("/")
        temp[-1] = self.dll_prefix + temp[-1] + self.dll_ext
        return "/".join(temp)
    
    def get_dll_files(self, dlls):
        return [self.get_file(dll) for dll in dlls]
    
file_util = FileUtil()
 
def check_file_timeout(dest_file, dependencies, ignore = ['__pycache__']):
    if dest_file is None:
        return True 
    if not os.path.exists(dest_file):
        return True
    file_mtime = os.stat(dest_file).st_mtime
    
    def check_file(file):
        if os.stat(file).st_mtime > file_mtime:
            return True
        return False
    
    def check_dir(dir):  
        for name in os.listdir(dir):
            if name in ignore:
                continue
            file = os.path.join(dir, name)
            if check(file):
                return True
        return False
    
    def check(file):
        if os.stat(file).st_mtime > file_mtime:
            return True
        if os.path.isdir(file):
            return check_dir(file)
        else:
            return check_file(file) 
        
    for file in dependencies:
        if check(file):
            return True
    return False
