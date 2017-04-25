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

python_source_lib = os.path.abspath(os.path.dirname(os.__file__))
 
class bundler(object):
    def __init__(self, dirname, zip_file = True):
        self.dirname = dirname
        self.zip_file = zip_file
        self.is_compress = False if zip_file is None else True 
        self.zip_files = []
        self.copy_files = []
        self.subpyd_files = {} #name, fullpath
        self.modules = []  #must use fullname, modules in the dictionary will be skipped
        #modules in the python dll, has not __file__ attr
        self.modules.append('itertools')
        self.modules.append('sys')
        self.modules.append('builtins') 
        if not os.path.exists(self.dirname):
            os.mkdir(self.dirname)
    def add_path(self, path):
        '''
        This method is not suggested, use add_module instead.
        '''
        if(os.path.isdir(path)):
            self.zip_files.append(path)
        else:
            tail = os.path.splitext(path)[1]
            if tail == '.py':
                self.zip_files.append(path)
            else:
                self.copy_files.append(path)            
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
            return
        self.modules.append(name)
        module = __import__(name)
        file = module.__file__
        if(file.endswith('__init__.py')):
            self.zip_files.append(os.path.dirname(file))
        elif(file.endswith('so') or file.endswith('dll') or file.endswith('pyd')):
            self.copy_files.append(file)
        else:
            self.zip_files.append(file)
    def bundle(self):
        self.bundle_init()
        self.compile_objs(self.zip_files, cdir = self.root,
                      ignore = ['__pycache__'])
        self.compress()
        self.copy()
    def bundle_init(self): 
        #folder init
        if self.is_compress: #create a temp folder
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
        for file in self.copy_files:
            shutil.copy(file, os.path.join(dirname, os.path.basename(file))) 
        for name, file in self.subpyd_files.items():
            shutil.copy(file, os.path.join(dirname, name)) 
            
    def compile_objs(self, files, cdir, ignore=['__pycache__'], 
                      maxlevels=10, ddir=None, optimize=-1, is_source = False):
        print('compile start')
        def _compile_obj(file):
            _file = os.path.abspath(file)
            if not os.path.exists(_file):
                success = False
                print("file '%s' not exist" % file)
                return success
            if os.path.isdir(_file):
                success = self.compile_dir(_file, cdir, ignore = ignore, 
                                      maxlevels=10, ddir=None, 
                                      optimize=-1, is_source = is_source)
            else:
                success = self.compile_file(_file, cdir, ddir, 
                                       optimize, is_source = is_source)
            return success
        success = True
        for file in files:
            print("compile file '%s'" % file)
            if "*" in file or "?" in file or "[" in file:
                _files = glob.glob(file)
                for file in _files:
                    print("--compile file '%s'" % file)
                    success = _compile_obj(file)
            else:
                success = _compile_obj(file)
            if not success:
                break
        if success:
            print('compile successed.')
        else:
            print('compile failed.')  
            
    def compile_file(self, fullname, cdir, ddir=None, optimize=-1, is_source = False):
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        elif not os.path.isdir(cdir):
            raise Exception('%s is not a folder' % cdir)
        name = os.path.basename(fullname)
        if ddir is not None:
            dfile = os.path.join(ddir, name)
        else:
            dfile = None
        tail = os.path.splitext(name)[1]
        if self.is_compress and tail in ['.so', '.dll', '.exe']:
            self.copy_files.append(fullname) #excluded from the zipfile
            return True
        elif self.is_compress and tail in ['.pyd']:
            arcname = os.path.relpath(cdir, self.root).replace("\\", ".").replace(r"/", ".")
            if arcname:
                pydname = '{0}.{1}'.format(arcname, name)
            else:
                pydname = name
            self.subpyd_files[pydname] = fullname #excluded from the zipfile
            return True
        elif is_source or tail != '.py': #copy directly
            cfile = os.path.join(cdir, name)
            print('copying file {0} to {1}'.format(fullname, cfile))
            shutil.copy(fullname, cfile) 
            return True
        try:
            cfile = os.path.join(cdir, name) + ('c' if __debug__ else 'o')
            print('compile file {0} to {1}'.format(fullname, cfile))
            py_compile.compile(fullname, cfile, dfile, True,
                                optimize=optimize)
            return True
        except Exception as ex:
            print('Exception: %s' % str(ex))
            return False
            
    def compile_dir(self, dir, cdir, ignore=['__pycache__'], 
                    maxlevels=10, ddir=None, 
                    optimize=-1, is_source = False):
        if cdir is None:
            cdir = os.path.abspath('.')
        if not os.path.exists(cdir):
            os.mkdir(cdir)
        elif not os.path.isdir(cdir):
            raise Exception('%s is not a folder' % cdir)
        name = os.path.basename(dir)
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
                success = self.compile_file(fullname, cdir, ddir, optimize, is_source = is_source)
                if not success:
                    return success
            elif (maxlevels > 0 and name != os.curdir and name != os.pardir and
                  os.path.isdir(fullname) and not os.path.islink(fullname)):
                success = self.compile_dir(fullname, cdir, 
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
     
def get_libcore(dirname, zip_file = r'libcore.zip'):
    '''
    Test for Python3.5
    '''
    lib = bundler(dirname, zip_file)
    lib.add_module('encodings')
    lib.add_module('collections')
    lib.add_module('traceback')
    lib.add_module('copyreg')
    lib.add_module('abc')
    lib.add_module('types')
    lib.add_module('locale')
    lib.add_module('functools')
    lib.add_module('sre_constants')
    lib.add_module('sre_parse')
    lib.add_module('_bootlocale')
    lib.add_module('linecache')
    lib.add_module('_collections_abc')
    lib.add_module('_weakrefset')
    lib.add_module('reprlib')
    lib.add_module('operator')
    lib.add_module('heapq')
    lib.add_module('io')
    lib.add_module('re')
    lib.add_module('sre_compile')
    lib.add_module('weakref')
    lib.add_module('keyword')
    lib.add_module('codecs')
    #site, may not need when Py_NoSiteFlag = 1?
    lib.add_module('site')
    lib.add_module('_sitebuiltins')
    lib.add_module('os')
    lib.add_module('stat')
    lib.add_module('ntpath')
    lib.add_module('genericpath')
    lib.add_module('sysconfig')
    return lib

def get_libext(dirname, zip_file = r'libext.zip'):
    libcore = get_libcore(dirname)
    libext = bundler(dirname, zip_file)
    libext.skip_modules(libcore.modules)
    return libext

def add_ctypes(self, libext):
    self.add_module('ctypes')
    self.add_module('_ctypes')
    libext.add_module('struct')
 
def add_numpy(self, libext):
    '''
    not working, because the 'multiarray' module
    '''
    self.add_module('numpy')
    #Windows Anaconda
    mkldir = os.path.join(sys.prefix, 'Library/bin')
    #WinPython
    #import numpy
    #mkldir = os.path.join(sys.prefix, os.path.join(numpy.__file__, "../core"))
    for mkl in ('libiomp5md', 'mkl_avx2', 'mkl_core', 'mkl_intel_thread', 'mkl_rt'):
        libext.add_path(mkldir + os.path.sep + mkl+'.dll')
    libext.add_module('__future__')
    libext.add_module('warnings')

def add_socket(self, libext):
    self.add_module('socket')
    self.add_module('_socket')