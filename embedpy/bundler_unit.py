import os
import time
import zipfile
import shutil
import py_compile
import glob
from _frozen_importlib_external import _NamespacePath

from .file_utils import file_util, check_file_timeout, \
    copy_file_if_newer, path_join_and_create

python_source_lib = os.path.abspath(os.path.dirname(os.__file__))
    
class BundlerUnit(object):
    def __init__(self, name : str, bundler : 'Bundler', 
                 is_compress = True, 
                 is_source = False, 
                 file_dir = None,
                 lib_dir = None, 
                 dll_dir = None,
                 pyd_dir = None):
        self.name = name        
        self.compile_files = [] #try to compile first
        self.dll_files = []
        self.subpyd_files = {} #name, fullpath
        self.copy_files = []
        self.bundler = bundler
        self.descriptor_cache = bundler.descriptor_cache
        self.module_cache = bundler.module_cache
        
        self.initialize(is_compress = is_compress, 
               is_source = is_source, 
               file_dir = file_dir,
               lib_dir = lib_dir, 
               dll_dir = dll_dir,
               pyd_dir = pyd_dir)
            
    def initialize(self, is_compress = False, 
               is_source = False,
               file_dir = None,
               lib_dir = None, 
               dll_dir = None,
               pyd_dir = None):
        self.file_dir = file_dir
        self.package_dir = file_dir if lib_dir is None else lib_dir
        self.is_source = is_source
        self.dll_dir = file_dir if dll_dir is None else dll_dir
        self.pyd_dir = file_dir if pyd_dir is None else pyd_dir
        self.is_compress = is_compress
     
    @property
    def zip_file(self):
        if self.is_compress:
            zip_file = "%s.zip" % self.name
        else:
            zip_file = None
        return zip_file
            
    def add_path(self, path, dest = None, ignore = ['__pycache__'], 
                 is_compile = None, is_override = False): 
        '''
        for .py file, the dest path is relative to self.package_dir
        '''
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
                if is_compile is None:
                    is_compile = True if path.endswith('.py') else False
                if is_compile:
                    self.compile_files.append((path, dest, ignore))    
                else:
                    self.copy_files.append((path, dest, is_override))
        else:
            if is_compile:
                self.compile_files.append((path, dest, ignore))   
            else:
                self.copy_files.append((path, dest, is_override))
                        
    def add_module(self, name, ignore = []):
        if '__pycache__' not in ignore:
            ignore.append('__pycache__')
        owner = self.module_cache.add_module(name, self.name)
        if owner is not None:
            print("des-{0} dependency '{1}' skipped, it has been added by des-{2}".format(self.name, name, owner))
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
        if hasattr(module, '__path__'):  # package
            path = module.__path__
            if isinstance(path, _NamespacePath):
                print(">>> It's a namespace package")
                path = path._path
            if len(path) == 0:
                self.add_path(module.__file__, ignore = ignore, is_compile = True)
                return
            elif len(path) > 1:
                raise Exception("package '{0}' has multiple path".format(name))
            path = path[0]
            #egg file or zipfile
            pa = os.path.dirname(path)
            if os.path.isfile(pa):
                print(">>> It's a zip file or egg file")
                self.add_path(pa, ignore = ignore, is_compile = True)
                return
            else:
                self.add_path(path, is_compile = True)
        else:
            self.add_path(module.__file__, ignore = ignore, is_compile = True)
            
    def add_descriptor(self, des):
        owner = self.descriptor_cache.add_module(des.name, self.name)
        if owner is not None:
            print("des-{0} dependency '{1}' skipped, it has been added by des-{2}".format(self.name, des.name, owner))
            return
        for name, ignore in des.modules:
            self.add_module(name, ignore)
        for dependency in des.dependencies:
            self.add_dependency(dependency)
        for path, dest, is_compile in des.paths:
            self.add_path(path, dest, is_compile = is_compile)
        
    def add_dependency(self, name):
        des = self.bundler.try_get_descriptor(name)
        if des is None:
            self.add_module(name)
        else:
            self.add_descriptor(des)
            
    def clear_package(self, name = None):
        '''
        only clear the package folder or zip file, not the dll, ext files
        '''
        if name is None:
            name = self.name
        if name == self.name and self.is_compress:
            zip_file = os.path.join(self.package_dir, self.zip_file)
            if os.path.exists(zip_file):
                os.remove(zip_file)
                return
        temp = os.path.join(self.package_dir, name)
        if os.path.exists(temp):
            shutil.rmtree(temp)

    def bundle(self, is_compress = None, is_source = None):
        print("bundle {0} start...".format(self.name))
        if is_compress is not None:
            self.is_compress = is_compress
        if is_source is not None:
            self.is_source = is_source
            
        if self.is_compress:
            dest_file = os.path.join(self.package_dir, self.zip_file)
            if not check_file_timeout(dest_file, 
                                      [bb[0] for bb in self.compile_files], 
                                      ignore = ['__pycache__']):
                print("%s reused." % dest_file)
                return
            
        self.__init_dir()        
        # compile all the files
        # files cannot be compiled will be put into the copy list
        self.compile_objs()
        self.compress()
        self.copy()
        
    def __init_dir(self): 
        #folder init
        if not os.path.exists(self.package_dir):
            os.mkdir(self.package_dir)
        if not os.path.exists(self.dll_dir):
            os.mkdir(self.dll_dir)
        if not os.path.exists(self.pyd_dir):
            os.mkdir(self.pyd_dir)
        
        if self.is_compress: # create a temp folder
            self.root = os.path.abspath('temp%d' % time.time())
        else:
            self.root = self.package_dir
        if not os.path.exists(self.root) or not os.path.isdir(self.root):
            os.mkdir(self.root)
            
    def compress(self):
        if not self.is_compress:
            return
        zip_file = os.path.join(self.package_dir, self.zip_file)
        print('bundle start %s' % zip_file) 
        compile_zip(zip_file, self.root, [])      
        print('bundle end') 
        print('remove the temp folder')
        shutil.rmtree(self.root)
                
    def copy(self):        
        for file, dest in self.dll_files:
            file_name = os.path.basename(file)
            dll_dir = path_join_and_create(self.dll_dir, dest)
            copy_file_if_newer(file, os.path.join(dll_dir, file_name))
        
        for name, file in self.subpyd_files.items():
            copy_file_if_newer(file, os.path.join(self.pyd_dir, name + '.pyd'))
        
        dirname = self.file_dir
        for file, dest, is_override in self.copy_files:
            if dest:
                destfile = os.path.join(dirname, dest)
                _dirname = os.path.dirname(destfile)
                if not os.path.exists(_dirname):
                    os.mkdir(_dirname)
            else:
                destfile = os.path.join(dirname, os.path.basename(file))
            if is_override:
                shutil.copy(file, destfile)
            else:
                copy_file_if_newer(file, destfile)
            
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
            
    def compile_file(self, fullname, cdir, newname = None, 
                     ddir = None, optimize = -1, is_source = False):
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