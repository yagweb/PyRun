'''
hand written descriptor for the platform module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return [build_platform(),
            build_multiprocessing(),]

def build_platform(des = None):
    if des is None:
        des = ModuleDescriptor('platform')
    des.add_module('platform')
    
    des.add_dependency('subprocess')
    return des

def build_multiprocessing(des = None):
    if des is None:
        des = ModuleDescriptor('multiprocessing')
    des.add_module('multiprocessing')
    return des