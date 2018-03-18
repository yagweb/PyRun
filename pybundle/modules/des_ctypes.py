'''
hand written descriptor for the ctypes module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_ctypes(), 

def build_ctypes(des = None):
    if des is None:
        des = ModuleDescriptor('ctypes')
    des.add_module('ctypes')
    des.add_module('_ctypes')
    
    des.add_dependency('struct')
    return des