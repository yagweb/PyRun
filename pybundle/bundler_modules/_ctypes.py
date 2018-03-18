# -*- coding: utf-8 -*-
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('ctypes'))

def build(des):
    des.add_module('ctypes')
    des.add_module('_ctypes')
    
    des.add_dependency('struct')
    return des