# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 16:14:04 2017
提取simupy中需要的文件到simupy-dist用于发布
@author: yagweb
"""
import os
import glob
import shutil
import platform
from collections import OrderedDict
from .bundler import file_util, copy_file_if_newer
        
class DirRecord(object):
    def __init__(self, name, root, is_exists):
        self.name = name
        self.fullname = os.path.join(root, name)
        self.dir_record = None
        self.is_exist = is_exists
    def __str__(self):
        return "0, %s" % self.name

class FileRecord(object):
    def __init__(self, name, root, is_exists):
        self.name = name
        self.fullname = os.path.join(root, name)
        self.dir_record = None
        self.is_exist = is_exists
    def __str__(self):
        return "1, %s" % self.name
    
def get_record(lineno, line, root):
    temp = line.split(",")
    if len(temp) != 2:
        raise Exception("error at %d" % lineno)
    _type = temp[0].strip()
    name = temp[1].strip()
    if _type == "0":
        return DirRecord(name, root, False)
    elif _type == "1":
        return FileRecord(name, root, False)
    else:
        raise Exception("error at %d" % lineno)

class StateFile(object):
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.path = os.path.join(root, ".dist")
        if not os.path.exists(self.path):
            raise Exception("folder '%s' is not a dist folder" % root)
        self.dir_records = OrderedDict()
        self.file_records = OrderedDict()
        with open(self.path, "r") as fp:
            for lineno, line in enumerate(fp.readlines()):
                if not line:
                    continue
                record = get_record(lineno, line, self.root)
                dir_name = os.path.dirname(record.name)
                if dir_name and dir_name not in self.dir_records:
                    print("***warning, at %d, parent dir not exist" % lineno)
                if isinstance(record, DirRecord):
                    self.dir_records[record.name] = record
                else:
                    self.file_records[record.name] = record
            
    def add_dir(self, fullname):
        fullname = os.path.abspath(fullname)
        name = os.path.relpath(fullname, self.root)
        #如果存在同名文件，先移除
        if name in self.file_records:
            if os.path.exists(name):
                print("remove file %s" % fullname)
                os.remove(fullname)
            del self.file_records[name]
            
        record = self.dir_records.get(name, None)
        if record:
            self.dir_records[name].is_exist = True
        else:
            print("+ new dir record %s" % fullname)
            self.dir_records[name] = DirRecord(name, self.root, True)
        
    def add_file(self, fullname):
        fullname = os.path.abspath(fullname)
        name = os.path.relpath(fullname, self.root)
        #如果存在同名文件夹，先移除
        if name in self.dir_records:
            if os.path.exists(name):
                print("remove folder %s" % fullname)
                shutil.rmtree(fullname)
            del self.dir_records[name]
                       
        record = self.file_records.get(name, None)
        if record:
            self.file_records[name].is_exist = True
        else:
            print("+ new file record %s" % fullname)
            self.file_records[name] = FileRecord(name, self.root, True)
        
    def update(self):
        dirs_not_exist = [bb for bb in self.dir_records.values() if not bb.is_exist]
        files_not_exist = [bb for bb in self.file_records.values() if not bb.is_exist]
        
        for record in dirs_not_exist:
            fullname = record.fullname
            print("remove dir record %s" % fullname)
            if os.path.exists(fullname):
                print("- remove folder %s" % fullname)
                shutil.rmtree(fullname)
            del self.dir_records[record.name]
            
        for record in files_not_exist:
            fullname = record.fullname
            print("- remove file record %s" % fullname)
            if os.path.exists(fullname):
                print("remove file %s" % fullname)
                os.remove(fullname)
            del self.file_records[record.name]
            
        with open(self.path, "w") as fp:
            for record in self.dir_records.values():
                fp.write(str(record))
                fp.write("\n")
            for record in self.file_records.values():
                fp.write(str(record))
                fp.write("\n")

class Publisher(object):
    def __init__(self, dest_folder):
        self.sources = []
        self.skip_files = ['__pycache__']
        self.skip_tails = []
        self.dest_folder = dest_folder
        self.state = StateFile(dest_folder)
    
    @staticmethod                
    def init(root):
        if not os.path.exists(root):
            os.mkdir(root)
        path = os.path.join(root, ".dist")
        fp = open(path, "w")
        fp.close()
        print("dist '%s' initialized" % root)
        
    def add_module(self, name, dest = None):
        if dest is None:
            dest = ''
        names = name.split(".")
        if len(names) == 1:
            module = __import__(name)
        else:
            module_name= names[-1]
            package_name = '.'.join(names[:-1])
            temp = {}
            exec("from {0} import {1}".format(package_name, module_name), temp)
            module = temp[module_name]
        file = os.path.dirname(module.__file__)
        if(file.endswith('__init__.py')):
            self.sources.append((os.path.dirname(file), dest))
        else:
            self.sources.append((file, dest))
    
    def add_path(self, path, dest = None):
        if dest is None:
            dest = os.path.basename(os.path.dirname(path))
        if not os.path.exists(path):
            raise Exception("'%s' not exists" % path)
        self.sources.append((path, dest))
        
    def update(self):
        success = True
        for source, dest in self.sources:
            if dest:
                root = os.path.join(self.dest_folder, dest)
            else:
                root = self.dest_folder
            if os.path.isdir(source):
                success = self.update_folder(source, root, None)
            else:
                success = self.update_file(source, root, None)
            if not success:
                break
        self.state.update()
        if not success:
            print("*********error*******")
            
    def update_folder(self, dir, cdir, newname = None, maxlevels = 1024):
        if cdir is None:
            cdir = os.path.abspath('.')
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        elif not os.path.isdir(cdir):
            raise Exception('%s is not a folder' % cdir)
        name = newname if newname else os.path.basename(dir)
        cdir = os.path.join(cdir, name)
        
        self.state.add_dir(cdir)
        
        print('updating folder {!r}...'.format(cdir))
        names = os.listdir(dir)    
        names.sort()
        success = True
        for name in names:
            if name in self.skip_files:
                print("skipped folder '%s'" % os.path.join(cdir, name))
                continue
            fullname = os.path.join(dir, name)
            if not os.path.isdir(fullname):
                success = self.update_file(fullname, cdir, None)
                if not success:
                    return success
            elif (maxlevels > 0 and name != os.curdir and name != os.pardir and
                  os.path.isdir(fullname) and not os.path.islink(fullname)):
                success = self.update_folder(fullname, cdir, None, maxlevels - 1)
                if not success:
                    return success
        return success
            
    def update_file(self, fullname, cdir, newname = None):         
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        elif not os.path.isdir(cdir):
            raise Exception('%s is not a folder' % cdir)
        name = newname if newname else os.path.basename(fullname)
        tail = os.path.splitext(name)[1]
        if tail in self.skip_tails or name in self.skip_files:
            print("skipped file '%s'" % fullname)
            return True
        else:
            cfile = os.path.join(cdir, name)       
            self.state.add_file(cfile)
            print('updating file {0}'.format(cfile), end = ', ')
            if not os.path.exists(cfile) or \
               os.stat(fullname).st_mtime > os.stat(cfile).st_mtime:
                shutil.copy(fullname, cfile)
                print("updated.")
            else:
                print("reused.")
            return True
        
class Package(object):
    def __init__(self):
        self.modules = {}
        self.files = []
            
    def add_binaries_in_package(self, name):
        module = __import__(name)
        folder = os.path.dirname(module.__file__)
        self.add_binaries_in_folder(folder, is_recusive = True)
        
    def add_file(self, path):
        if not os.path.exists(path):
            raise Exception('file %s not exist' % path)
        self.files.append(path)
        
    def add_dll_file(self, name):
        path = file_util.get_dll_file(name)
        self.add_file(path)

    def add_binaries_in_folder(self, folder, is_recusive = True):
        root = os.path.dirname(folder)
        if is_recusive:
            self.__add_folder_recusive(folder, root)
            return
        
        if platform.system() == "Windows":
            fmt = os.path.join(folder, "*.pyd")
            for bb in glob.glob(fmt):
                self.__add_module(bb, root)
            
            fmt = os.path.join(folder, "*.dll")
            for bb in glob.glob(fmt):
                self.files.append(bb)
        else:
            fmt = os.path.join(folder, "*.so")            
            for bb in glob.glob(fmt):
                self.__add_binary(bb, root)
            
    def __add_binary(self, file, root):
        '''
        binary: 分为dll和pyd
        '''
        temp = os.path.basename(file).split(".")
        if len(temp) > 2: #it's a module, not a dll
            self.__add_module(file, root)
        else:
            self.files.append(file)
            
    def __add_module(self, path, root_folder):
        source = os.path.relpath(path, root_folder)
        source = os.path.join(os.path.dirname(source), 
                           os.path.basename(source).split(".")[0])
        dirname = os.path.dirname(source).replace("\\", "/").replace("/", ".") + "."
        basename = os.path.basename(source).split(".")[0] + ".pyd"
        dest_file = dirname + basename
        self.modules[dest_file] = path
    
    def __add_folder_recusive(self, folder, root):
        mod_ext = file_util.mod_ext
        dll_ext = file_util.dll_ext
        for folder, dirs, files in os.walk(folder, topdown = False):
            for name in files:
                if name.endswith(mod_ext):
                    bb = os.path.join(folder, name)
                    self.__add_module(bb, root)
                elif name.endswith(dll_ext):
                    bb = os.path.join(folder, name)
                    self.files.append(bb)
                    
    def save(self, dest_root): 
        # create folder if not exist
        if not os.path.exists(dest_root):
            temp = os.path.dirname(dest_root)
            if not os.path.exists(temp):
                os.mkdir(temp)
            os.mkdir(dest_root)
        
        #save modules
        for dest_file, source in self.modules.items():
            copy_file_if_newer(source, os.path.join(dest_root, dest_file))
        
        #save files
        for source in self.files:
            dest_file = os.path.join(dest_root, os.path.basename(source))
            copy_file_if_newer(source, dest_file)