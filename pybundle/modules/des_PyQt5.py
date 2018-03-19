'''
hand written descriptor for the PyQt5 module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_PyQt5(), 

def build_PyQt5(des = None):
    if des is None:
        des = ModuleDescriptor('PyQt5')
    des.add_module('PyQt5', ignore = ['port_v2'])
    
    des.add_dlls_in_library_bin(['Qt5Core', 'Qt5Gui', 'Qt5Widgets'])
#    des.add_path("Qt5*", is_glob = True)
    des.add_dlls_in_library_bin(['api-ms-win-crt-multibyte-l1-1-0', 
                                 'api-ms-win-crt-utility-l1-1-0'])
    des.add_dlls_in_library_bin(['Enginio', 'freetype', 'icudt58'])
    des.add_dlls_in_library_bin(['icuin58', 'icuuc58', 'libifcoremd'])
    des.add_dlls_in_library_bin(['libiomp5md', 'libjpeg', 'libmmd'])
    des.add_dlls_in_library_bin(['libpng16', 'msvcp140', 'zlib'])
    
    # fixed: could not find or load the Qt platform plugin "windows"
    # need to copy with folder and put as the same level with the exe
    des.add_path('Library/plugins/platforms/qwindows.dll', 
                 '../platforms', is_relative = True)
        
    #
    des.add_dependency('sip')
    des.add_dependency('pygments')
    return des