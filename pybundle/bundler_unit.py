# -*- coding: utf-8 -*-
"""
@author: YangWenguang
Issues contact with: hbtmdxywg@126.com
"""
import os
import sys
import time
import zipfile
import shutil
import py_compile
import glob

from .file_utils import file_util, check_file_timeout, \
    copy_file_if_newer, path_join_and_create

python_source_lib = os.path.abspath(os.path.dirname(os.__file__))

class ModuleList(object):
    '''
    shared by multiple Bundlers
    '''
    def __init__(self):
        self.modules = []  #must use fullname, modules in the dictionary will be skipped
        # modules in the python dll, has not __file__ attr
        self.modules.append('itertools')
        self.modules.append('sys')
        self.modules.append('builtins') 
        self.modules.append('time') 
        
    def skip_module(self, name):
        if name in self.modules:
            return
        self.modules.append(name)
        
    def skip_modules(self, names):        
        for name in names:
            if name in self.modules:
                continue
            self.modules.append(name)    
        
    def add_module(self, name):
        if name in self.modules:
            return False
        self.modules.append(name) 
        return True
    
class BundlerUnit(object):
    def __init__(self, name : str, bundler : 'Bundler', 
                 is_compress = True, 
                 is_source = False, 
                 is_clear = False, 
                 lib_dir = None, 
                 dll_dir = None,
                 pyd_dir = None):
        self.name = name        
        self.compile_files = [] #try to compile first
        self.dll_files = []
        self.subpyd_files = {} #name, fullpath
        self.copy_files = []
        self.bundler = bundler
        self.modules = bundler.modules
        
        self.initialize(is_compress = is_compress, 
               is_source = is_source, is_clear = is_clear, 
               lib_dir = lib_dir, 
               dll_dir = dll_dir,
               pyd_dir = pyd_dir)
            
    def initialize(self, is_compress = False, 
               is_source = False, is_clear = False, 
               lib_dir = None, 
               dll_dir = None,
               pyd_dir = None):
        self.dirname = lib_dir
        self.is_source = is_source
        self.is_clear = is_clear
        self.dll_dir = lib_dir if dll_dir is None else dll_dir
        self.pyd_dir = lib_dir if pyd_dir is None else pyd_dir
        self.is_compress = is_compress
     
    @property
    def zip_file(self):
        if self.is_compress:
            zip_file = "%s.zip" % self.name
        else:
            zip_file = None
        return zip_file
            
    def add_path(self, path, dest = None, ignore = ['__pycache__']): 
        if not os.path.exists(path):
            raise Exception("file %s not exists" % path)
        if os.path.isfile(path):
            if path.endswith(file_util.mod_ext):
                mod_name = file_util.get_mod_name(path)
                self.subpyd_files[mod_name] = path
            elif path.endswith('.pyd'):
                file_name = os.path.basename(path)
                mod_name = file_name[:len(file_name) - 4]
                self.subpyd_files[mod_name] = path
            elif path.endswith(file_util.dll_ext):
                self.dll_files.append((path, dest))
            else:
                self.compile_files.append((path, dest, ignore))                
        else:
            self.compile_files.append((path, dest, ignore))
                        
    def add_module(self, name, ignore = []):
        if '__pycache__' not in ignore:
            ignore.append('__pycache__')
        if not self.modules.add_module(name):
            return
        names = name.split(".")
        if len(names) == 1:
            module = __import__(name)
        else:
            module_name = names[-1]
            package_name = '.'.join(names[:-1])
            temp = {}
            exec("from {0} import {1}".format(package_name, module_name), temp)
            module = temp[module_name]
        path = module.__file__
        if(path.endswith('__init__.py')):
            path = os.path.dirname(path) 
        self.add_path(path, ignore = ignore)
            
    def add_descriptor(self, des):
        for name, ignore in des.modules:
            self.add_module(name, ignore)
        for dependency in des.dependencies:
            self.add_dependency(dependency)
        for path, dest in des.paths:
            self.add_path(path, dest)
        
    def add_dependency(self, name):
        des = self.bundler.try_get_descriptor(name)
        if des is None:
            self.add_module(name)
        else:
            self.add_descriptor(des)

    def bundle(self, is_compress = None, is_clear = None):
        if is_compress is not None:
            self.is_compress = is_compress
        if is_clear is not None:
            self.is_clear = is_clear
            
        if self.is_compress:
            dest_file = os.path.join(self.dirname, self.zip_file)
            if self.is_clear and os.path.exists(dest_file):
                os.remove(dest_file)
            elif not check_file_timeout(dest_file, 
                                      [bb[0] for bb in self.compile_files], 
                                      ignore = ['__pycache__']):
                print("%s reused." % dest_file)
                return
            
        self.__init_dir()        
        # 编译所有py文件，要拷贝的，放入copy目录中
        self.compile_objs()
        self.compress()
        #拷贝其他文件
        self.copy()
        
    def __init_dir(self): 
        #folder init
        if not os.path.exists(self.dirname):
            os.mkdir(self.dirname)
        if not os.path.exists(self.dll_dir):
            os.mkdir(self.dll_dir)
        if not os.path.exists(self.pyd_dir):
            os.mkdir(self.pyd_dir)
        
        if self.is_compress: # create a temp folder
            self.root = os.path.abspath('temp%d' % time.time())
        else:
            self.root = self.dirname
        if not os.path.exists(self.root) or not os.path.isdir(self.root):
            os.mkdir(self.root)
            
    def compress(self):
        if not self.is_compress:
            return
        zip_file = os.path.join(self.dirname, self.zip_file)
        print('bundle start %s' % zip_file) 
        compile_zip(zip_file, self.root, [])      
        print('bundle end') 
        print('remove the temp folder')
        shutil.rmtree(self.root)
                
    def copy(self):
        dirname = self.dirname
        
        #dll 文件处理
        for file, dest in self.dll_files:
            file_name = os.path.basename(file)
            dll_dir = path_join_and_create(self.dll_dir, dest)
            copy_file_if_newer(file, os.path.join(dll_dir, file_name))
        
        for name, file in self.subpyd_files.items():
            copy_file_if_newer(file, os.path.join(self.pyd_dir, name + '.pyd'))
        
        for file, dest in self.copy_files:
            if dest:
                destfile = os.path.join(dirname, dest)
                _dirname = os.path.dirname(destfile)
                if not os.path.exists(_dirname):
                    os.mkdir(_dirname)
                copy_file_if_newer(file, destfile) 
            else:
                copy_file_if_newer(file, os.path.join(dirname, os.path.basename(file))) 
            
    def compile_objs(self, maxlevels = 10, ddir = None, optimize = -1):
        files = self.compile_files
        cdir = self.root
        is_source = self.is_source
        print('bundle %s start' % self.name)
        def _compile_obj(file, cdir, newname, ignore):
            _file = os.path.abspath(file)
            if not os.path.exists(_file):
                success = False
                print("file '%s' not exist" % file)
                return success
            if os.path.isdir(_file):
                #should skip if folder is module and exist?
                temp = os.path.join(self.root, os.path.basename(_file))
                if not self.is_compress and os.path.exists(temp):                    
                    if self.is_clear:
                        shutil.rmtree(temp)
                        os.mkdir(temp)
                    else:
                        print('skipping %s' % _file)
                        return True
                success = self.compile_dir(_file, cdir, newname, ignore = ignore, 
                                      maxlevels=10, ddir=None, 
                                      optimize=-1, is_source = is_source)
            else:
                success = self.compile_file(_file, cdir, newname, ddir, 
                                       optimize, is_source = is_source)
            return success
        success = True
        for file, dest, ignore in files:
            if dest:
                newname = os.path.basename(dest)
                _cdir = os.path.join(cdir, os.path.dirname(dest)) 
            else :
                _cdir = cdir
                newname = None
#            print("compile file '%s'" % file)
            if "*" in file or "?" in file or "[" in file:
                _files = glob.glob(file)
                for file in _files:
                    print("--compile file '%s'" % file)
                    success = _compile_obj(file, _cdir, newname, ignore)
            else:
                success = _compile_obj(file, _cdir, newname, ignore)
            if not success:
                break
        if success:
            print('bundle %s successed.' % self.name)
        else:
            print('bundle %s failed.' % self.name)  
            
    def compile_file(self, fullname, cdir, newname = None, ddir=None, optimize = -1, is_source = False):
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        elif not os.path.isdir(cdir):
            raise Exception('%s is not a folder' % cdir)
        name = newname if newname else os.path.basename(fullname)
        if ddir is not None:
            dfile = os.path.join(ddir, name)
        else:
            dfile = None
        tail = os.path.splitext(name)[1]
        if '~' in tail: #".c~c":
#            print('skipping file {0}'.format(fullname))
            return True
        if self.is_compress:
            for mod_ext in [file_util.mod_ext, '.pyd']:
                if name.endswith(mod_ext):
                    name = name[:len(name) - len(mod_ext)]
                    arcname = os.path.relpath(cdir, self.root).replace("\\", ".").replace(r"/", ".")
                    if arcname:
                        pydname = '{0}.{1}'.format(arcname, name)
                    else:
                        pydname = name
                    self.subpyd_files[pydname] = fullname #excluded from the zipfile
                    return True
            if name.endswith(file_util.dll_ext):
                self.dll_files.append(fullname) #excluded from the zipfile
                return True
        if is_source or tail != '.py': #copy directly
            cfile = os.path.join(cdir, name)
            print('copying file {0} to {1}'.format(fullname, cfile))
            shutil.copy(fullname, cfile) 
            return True
        try:
            cfile = os.path.join(cdir, name) + ('c' if __debug__ else 'o')
            if is_source_remained(fullname, cfile):
                print('skipping py file {0}'.format(fullname))
                return True
            print('compile file {0} to {1}'.format(fullname, cfile))
            py_compile.compile(fullname, cfile, dfile, True,
                                optimize=optimize)
            return True
        except Exception as ex:
            print('Exception: %s' % str(ex))
            return False
            
    def compile_dir(self, dir, cdir, newname = None, ignore = ['__pycache__'], 
                    maxlevels=10, ddir=None, 
                    optimize=-1, is_source = False):
        if cdir is None:
            cdir = os.path.abspath('.')
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        elif not os.path.isdir(cdir):
            raise Exception('%s is not a folder' % cdir)
        name = newname if newname else os.path.basename(dir)
        cdir = os.path.join(cdir, name)
        print('Listing {!r}...'.format(dir))
        names = os.listdir(dir)    
        names.sort()
        success = True
        for name in names:
            if name in ignore:
                continue
            fullname = os.path.join(dir, name)
            if not os.path.isdir(fullname):
                success = self.compile_file(fullname, cdir, None, ddir, optimize, is_source = is_source)
                if not success:
                    return success
            elif (maxlevels > 0 and name != os.curdir and name != os.pardir and
                  os.path.isdir(fullname) and not os.path.islink(fullname)):
                success = self.compile_dir(fullname, cdir, None,
                                      ignore, maxlevels - 1, 
                                      ddir, optimize, is_source = is_source)
                if not success:
                    return success
        return success
   
def compile_zip(path, dir, excludes = []):
    #zpfd = zipfile.ZipFile(path, mode='w', compression=zipfile.ZIP_DEFLATED)
    zpfd = zipfile.ZipFile(path, mode='w')
    def zip_dir(_dir):
        for dirpath, dirnames, filenames in os.walk(_dir, True):
            for filename in filenames:
                fullname = os.path.join(dirpath, filename)
                arcname = os.path.relpath(fullname, dir)
                print('Add... ' + arcname)
                zpfd.write(fullname, arcname)        
    if len(excludes) == 0:
        zip_dir(dir)
    else:
        for _file in os.listdir(dir):
            if _file in excludes:
                continue
            fullname = os.path.join(dir, _file)
            if os.path.isdir(fullname):
                zip_dir(fullname)
            else:
                arcname = os.path.relpath(fullname, dir)
                print('Add... ' + arcname)
                zpfd.write(fullname, arcname)
    zpfd.close()    
            
def delete_from_zip(zip_path, delete_dirs, delete_files=[]):
    print('delete from zip file')
    zin = zipfile.ZipFile (zip_path, 'r')
    new_zipfile = zip_path + '.temp.zip' #create a new file
    zout = zipfile.ZipFile (new_zipfile, 'w')
    for item in zin.infolist():
#        print(item.filename)
        temp = os.path.dirname(item.filename)
        dirname = temp
        while temp:
            dirname = temp
            temp = os.path.dirname(dirname)
        if dirname in delete_dirs or item.filename in delete_files:  #remove the file
            continue
        buffer = zin.read(item.filename)
        zout.writestr(item, buffer) #write file into the zip
    zout.close()
    zin.close()     
    #override, if the file existed
    shutil.move(new_zipfile, zip_path) 

def is_source_remained(source, dest):
    if not os.path.exists(dest) or \
        os.stat(source).st_mtime > os.stat(dest).st_mtime:
            return False
    return True