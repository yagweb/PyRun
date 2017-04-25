# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 18:12:19 2013
Anaconda x64: module 'dis' has no attribute '_unpack_opargs'
WinPython x86 passed.

solution for some compile errors:
    1 No module named 'mpl_toolkits' : the package imported by cx_Freeze must has a file '__init__', manually add one
    2 No module named 'scipy' :
        bug:Find the hooks.py file in cx_freeze folder. Change line 548 from finder.
        IncludePackage("scipy.lib") to finder.IncludePackage("scipy._lib").

@author: yagweb
"""
import os
from cx_Freeze import setup, Executable

def get_files(folders):
    files = []
    for folder, relative_path in folders:
        for file in os.listdir(folder):
            f1 = os.path.join(folder, file)
            if os.path.isfile(f1):  # skip directories
                files.append((f1, os.path.join(relative_path, file)))    
    return files
    
def build(dest_path):
    import numpy
    ETS_folder = os.path.abspath(os.path.join(numpy.__file__, "../../"))
    mkldir = "%s/numpy/core" % ETS_folder 
    #include_files files in folder will be added automatically
    include_files = [] #item can be str or (str, str).former is relative path to this script, 
#    binaries = [(mkldir + "/" + mkl, mkl) for mkl in os.listdir(mkldir) \
#                if mkl.startswith('mkl_') or mkl=='libiomp5md.dll']
    binaries = [(mkldir + os.path.sep + mkl+'.dll', mkl+'.dll') for mkl in ('libiomp5md', 'mkl_avx2', 'mkl_core', 'mkl_intel_thread', 'mkl_p4', 'mkl_rt')]
    include_files.extend(binaries)
    #(matplotlib.get_data_path(), "mpl-data")
    
    folders = [("%s\\pyface\\images\\" % ETS_folder, "pyface\\images"),
               ("%s\\pyface\\ui\\qt4\\images" % ETS_folder, "pyface\\ui\\qt4\\images"),
               ("%s\\pyface\\ui\\qt4\\workbench\\images" % ETS_folder, r"pyface\ui\qt4\workbench\images"),
               (r"%s\traitsui\qt4\images" % ETS_folder, r"traitsui\qt4\images"),
               (r"%s\traitsui\image\library" % ETS_folder, r"traitsui\image\library"),
               ]
    zip_includes = get_files(folders)
    
    build_exe_options = {"build_exe" : dest_path,
                         "include_msvcr" : True,
                         "packages": ["pyface.ui.qt4",
                                      "traitsui.qt4",
                                      "matplotlib.backends.backend_qt4agg",
                                      "matplotlib.backends.backend_tkagg", 
                                      "tkinter.filedialog", 
                                      "mpl_toolkits",
                                      "scipy"],
                         "excludes": ['IPython', 'tornado'],
                         "zip_includes" : zip_includes,
                         "include_files": include_files
                         }
    
    base = None
    executables = [
        Executable('PyRunCx.py', 
                   targetName="PyRun.exe", 
                   #icon = "Machine.ico",
                   base=base),
    ]
    
    setup(name='PyRun',
          version='1.0',
          description='cx_Freeze test',
          options = {"build_exe": build_exe_options},
          executables = executables
          ) 
    
if __name__ == '__main__': 
    import sys
    import shutil
    sys.argv.append('build')
    print('build start.')
    dest_path = r'..\tmp\PyRun'
#    build(dest_path)
    shutil.copy("PyRun.py", os.path.join(dest_path, "PyRun.py"))
    print('build end.')
    