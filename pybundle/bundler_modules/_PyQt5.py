# -*- coding: utf-8 -*-
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('PyQt5'))

def build(des):
    des.add_module('PyQt5', ignore = ['port_v2'])
    
    des.add_dlls_in_library_bin(['Qt5Core', 'Qt5Gui', 'Qt5Widgets'])
#    des.add_path("Qt5*", is_glob = True)
    
    # fixed: could not find or load the Qt platform plugin "windows"
    # need to copy with folder and put as the same level with the exe
    des.add_path('Library/plugins/platforms/qwindows.dll', 
                 '../platforms', is_relative = True)
        
    #
    des.add_dependency('sip')
    return des