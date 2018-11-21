'''
hand written descriptor for the platform module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return [build_platform(),
            build_threading(),
            build_multiprocessing(),]

def build_platform(des = None):
    if des is None:
        des = ModuleDescriptor('platform')
    des.add_module('platform')
    
    des.add_dependency('subprocess')
    return des

def build_threading(des = None):
    if des is None:
        des = ModuleDescriptor('threading')
    des.add_module('threading')
    return des

def build_multiprocessing(des = None):
    if des is None:
        des = ModuleDescriptor('multiprocessing')
    des.add_module('multiprocessing')
    des.add_module('_multiprocessing')
    
    des.add_dependency('threading')
    des.add_dependency('signal')
    des.add_dependency('socket')
    des.add_dependency('queue')
    des.add_dependency('runpy')
    return des