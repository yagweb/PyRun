# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 18:12:19 2013
Anaconda 3.5 x64: module 'dis' has no attribute '_unpack_opargs'
WinPython 3.4 x86 passed.

solution for some compile errors:
    1 No module named 'mpl_toolkits' : the package imported by cx_Freeze must has a file '__init__', manually add one
    2 No module named 'scipy' :
        bug:Find the hooks.py file in cx_freeze folder. Change line 548 from finder.
        IncludePackage("scipy.lib") to finder.IncludePackage("scipy._lib").

It's not a good idea to use freezer:
    打包后，900M！！
    自动模块搜索并不智能！eg，一些复杂的模块也要手动处理
    库不全，修改后重新运行，又怎么拷贝，我只想更新某个模块而已

    bundler,而不是用Freezer，不自动找模块，程序员自己定义：
    
    动态生成一个main.c，调用编译器编译
    DLLs - 目录，exe启动时修改环境变量，hooks找扩展模块，zip和egg中的模块等。

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
    
class Freezer():
    def __init__(self):
        #include_files files in folder will be added automatically
        #type of item can be str or (str, str).former is relative path to this script
        self.include_files = []
        self.zip_includes = []
        self.packages = []
        self.executables = []
    
    def add_numpy(self):
        import numpy
        ETS_folder = os.path.abspath(os.path.join(numpy.__file__, "../../"))
        mkldir = "%s/numpy/core" % ETS_folder 
#        binaries = [(mkldir + "/" + mkl, mkl) for mkl in os.listdir(mkldir) \
#                    if mkl.startswith('mkl_') or mkl=='libiomp5md.dll']
        binaries = [(mkldir + os.path.sep + mkl+'.dll', mkl+'.dll') \
                    for mkl in ('libiomp5md', 'mkl_avx2', 'mkl_core', 'mkl_intel_thread', 'mkl_p4', 'mkl_rt')]
        self.include_files.extend(binaries)
    
    def add_traitsui(self):
        import traitsui
        ETS_folder = os.path.abspath(os.path.join(traitsui.__file__, "../../"))
        folders = [("%s\\pyface\\images\\" % ETS_folder, "pyface\\images"),
                   ("%s\\pyface\\ui\\qt4\\images" % ETS_folder, "pyface\\ui\\qt4\\images"),
                   ("%s\\pyface\\ui\\qt4\\workbench\\images" % ETS_folder, r"pyface\ui\qt4\workbench\images"),
                   (r"%s\traitsui\qt4\images" % ETS_folder, r"traitsui\qt4\images"),
                   (r"%s\traitsui\image\library" % ETS_folder, r"traitsui\image\library"),
                   ]
        self.zip_includes.extend(get_files(folders))
        self.packages.extend(["pyface.ui.qt4",
                              "traitsui.qt4"])
    
    def add_matplotlib(self):
        #(matplotlib.get_data_path(), "mpl-data")
        self.packages.extend(["matplotlib.backends.backend_qt4agg",
                              "matplotlib.backends.backend_tkagg", 
                              "tkinter.filedialog", 
                              "mpl_toolkits"])
        
    def add_package(self, name): 
        #scipy, socket etc.
        self.packages.append(name) 
        
    def add_executable(self, targetName, icon = None, base = None, startscript = None):
        if startscript is None:
            startscript = os.path.join(__file__, '../PyRunCx.py')
        self.executables.append(
                       Executable(startscript, 
                       targetName = targetName, 
                       icon = icon,
                       base = base))
    
    def build(self, name, dest_path, version = '1.0', description = '', startscript = None):
        build_exe_options = {"build_exe" : dest_path,
                             "include_msvcr" : True,
                             "packages": self.packages,
                             "excludes": ['IPython', 'tornado'],
                             "zip_includes" : self.zip_includes,
                             "include_files": self.include_files
                             }
                             
        if len(self.executables) == 0:
            self.add_executable("%s.exe" % name)
                
        setup(name = name,
              version = version,
              description = description,
              options = {"build_exe": build_exe_options},
              executables = self.executables
              )     