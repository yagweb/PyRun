# -*- coding: utf-8 -*-
"""
@author: YangWenguang
Issues contact with: hbtmdxywg@126.com
"""
import os
import time
import zipfile
import shutil
import py_compile
import glob

def compile_files(files, cdir=None, ignore=[], 
                  maxlevels=10, ddir=None, optimize=-1, 
                  zip_file = None, is_source = False):   
    if zip_file is not None:
        dirname = os.path.dirname(zip_file)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    if cdir is None:
        cdir_remove = True
        cdir = os.path.abspath('temp%d' % time.time())
    else:
        cdir_remove = False
    if not os.path.exists(cdir):
        os.mkdir(cdir)
    elif not os.path.isdir(cdir):
        raise Exception('%s is not a folder' % cdir)
    cdir_files = os.listdir(cdir)
    print('compile start')
    def _compile_file(file):
        _file = os.path.abspath(file)
        name = os.path.basename(_file)
        if name in cdir_files:
            cdir_files.remove(name)
        if not os.path.exists(_file):
            success = False
            print("file '%s' not exist" % file)
            return success
        if os.path.isdir(_file):
            success = compile_dir(_file, cdir, ignore = ignore, 
                                  maxlevels=10, ddir=None, 
                                  optimize=-1, is_source = is_source)
        else:
            success = compile_file(_file, cdir, ddir, 
                                   optimize, is_source = is_source)
        return success
    for file in files:
        print("compile file '%s'" % file)
        if "*" in file or "?" in file or "[" in file:
            _files = glob.glob(file)
            for file in _files:
                print("--compile file '%s'" % file)
                success = _compile_file(file)
        else:
            success = _compile_file(file)
        if not success:
            break
    if success:
        print('compile successed.')
    else:
        print('compile failed.')
        if cdir_remove:
            cdir = shutil.rmtree(cdir)
        return
        
    if zip_file is not None:
        print('bundle start')
        compile_zip(zip_file, cdir, cdir_files)      
        print('bundle end') 
    if cdir_remove:   
        print('remove the temp folder')
        cdir = shutil.rmtree(cdir)
   
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
        
def compile_dir(dir, cdir, ignore=[], 
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
            success = compile_file(fullname, cdir, ddir, optimize, is_source = is_source)
            if not success:
                return success
        elif (maxlevels > 0 and name != os.curdir and name != os.pardir and
              os.path.isdir(fullname) and not os.path.islink(fullname)):
            success = compile_dir(fullname, cdir, 
                                  ignore, maxlevels - 1, 
                                  ddir, optimize, is_source = is_source)
            if not success:
                return success
    return success
    
def compile_file(fullname, cdir, ddir=None, optimize=-1, is_source = False):
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
    if tail in ['.so', '.dll', '.pyd', '.exe']:
        print('skip file {0}'.format(fullname))
        return True
    elif is_source or tail != '.py':
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

def delete_from_zip(zip_path, delete_dirs, delete_files=[]):
    import zipfile
    import shutil
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
    
def get_libcore_files():
    '''
    Python3.5
    '''
    files = ['encodings/',
             'collections/',
             'traceback.py',
             'copyreg.py',
             'abc.py',
             'types.py',
             'locale.py',
             'functools.py',
             'sre_constants.py',
             'sre_parse.py',
             '_bootlocale.py',
             'linecache.py',
             '_collections_abc.py',
             '_weakrefset.py',
             'reprlib.py',
             'operator.py',
             'heapq.py',
             'io.py',
             're.py',
             'sre_compile.py',
             'weakref.py',
             'keyword.py',
             'codecs.py',
             #site
             'site.py',
                 '_sitebuiltins.py',
                 'os.py',
                 'stat.py',
                 'ntpath.py',
                 'genericpath.py',
                 'sysconfig.py',
             ]
    #itertools, sys，builtins etc are in the python dll
    return files

def test_bundle():
#    compile_zip('temp.zip', r'C:\Users\yagweb\work\git\pydata\test')
    compile_file(r'C:\Users\yagweb\work\git\StarKE\Lib\types.py', 
                            cdir=r'C:\Users\yagweb\work\git\StarKE\Scripts\temp')
#    compile_dir(r'C:/Users/yagweb/work/git/netcheck/netcheckui', 
#                            cdir=r'C:\Users\yagweb\work\git\StarKE\Scripts\temp1')
#    compile_files([r'C:/Users/yagweb/work/git/netcheck/netcheck',
#                   r'C:/Users/yagweb/work/git/netcheck/autoping.py'], 
#                            zip_file=r'temp.zip')
    
if __name__ == '__main__':
    test_bundle()