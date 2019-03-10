'''
hand written descriptor for the PyQt5 module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_PySide2(), 

def build_PySide2(des = None):
    if des is None:
        des = ModuleDescriptor('PySide2')
    des.is_compressable = False
    des.add_module('PySide2', ignore = ['include', 'Qt5WebEngineCore.dll'])
    
#    des.add_dlls_in_library_bin(['Qt5Core', 'Qt5Gui', 'Qt5Widgets'])
#    des.add_path("Qt5*", is_glob = True)
    des.add_dll_in_root('python3')
        
    #
    des.add_dependency('sip')
    des.add_dependency('shiboken2')
    return des