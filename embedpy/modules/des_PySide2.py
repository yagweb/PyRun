'''
hand written descriptor for the PyQt5 module
'''
import os
from .descriptor import ModuleDescriptor


def get_descriptors():
    return build_PySide2(), build_PySide2_QtWebEngine()


def build_PySide2(des = None):
    if des is None:
        des = ModuleDescriptor('PySide2')
    des.is_compressable = False
    des.add_module('PySide2', ignore = ['include', 'Qt5WebEngineCore.dll'])
    
#    des.add_dlls(['Qt5Core', 'Qt5Gui', 'Qt5Widgets'])
#    des.add_path("Qt5*", is_glob = True)
    des.add_dll('python3')
        
    #
    des.add_dependency('sip')
    des.add_dependency('shiboken2')
    return des 


def build_PySide2_QtWebEngine(des = None):
    if des is None:
        des = ModuleDescriptor('PySide2-QtWebEngine')
    des.is_compressable = False
    des.add_module('PySide2', ignore = ['include', "resources"])
    
#    des.add_dlls(['Qt5Core', 'Qt5Gui', 'Qt5Widgets'])
#    des.add_path("Qt5*", is_glob = True)
    des.add_dll('python3')
        
    #
    des.add_dependency('sip')
    des.add_dependency('shiboken2')
    des.add_dependency('typing') #for shiboken2
    des.add_dependency('zipfile')
    des.add_dependency('shutil')
    des.add_dependency('fnmatch')
    des.add_dependency('posixpath')
    des.add_dependency('struct')
    des.add_dependency('multiprocessing')
    return des