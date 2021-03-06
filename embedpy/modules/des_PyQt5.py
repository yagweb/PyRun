'''
hand written descriptor for the PyQt5 module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_PyQt5(), 

def build_PyQt5(des = None):
    if des is None:
        des = ModuleDescriptor('PyQt5')
    des.is_compressable = False
    des.add_module('PyQt5', ignore = ['port_v2'])
    
    des.add_dlls(['Qt5Core', 'Qt5Gui', 'Qt5Widgets'])
#    des.add_path("Qt5*", is_glob = True)
    des.add_dlls(['api-ms-win-crt-multibyte-l1-1-0', 
                  'api-ms-win-crt-utility-l1-1-0'])
    des.add_dlls(['Enginio', 'libifcoremd'])
    if des.python_version >= '3.6.4':
        des.add_dlls(['freetype', 'icudt58', 'icuin58', 'icuuc58'])
    else:
        des.add_dlls(['icudt57', 'icuin57', 'icuuc57'])
    des.add_dlls(['libiomp5md', 'libjpeg', 'libmmd'])
    des.add_dlls(['libpng16', 'msvcp140', 'zlib'])
    
    # fixed: could not find or load the Qt platform plugin "windows"
    # need to copy with folder and put as the same level with the exe
    des.add_path('Library/plugins/platforms/qwindows.dll', 
                 '../platforms', is_relative = True)
        
    #
    des.add_dependency('sip')
    des.add_dependency('pygments')
    return des