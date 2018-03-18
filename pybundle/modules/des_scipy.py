'''
hand written descriptor for the scipy module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_scipy(), 

def build_scipy(des = None):
    if des is None:
        des = ModuleDescriptor('scipy')
    des.add_module('scipy')
    
    # 
    des.add_dependency('numpy')
    des.add_dependency('multiprocessing')
    return des
    
