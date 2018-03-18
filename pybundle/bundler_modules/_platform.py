
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('platform'))

def build(des):
    des.add_module('platform')
    
    des.add_dependency('subprocess')
    return des