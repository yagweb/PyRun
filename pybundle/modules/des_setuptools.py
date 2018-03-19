'''
hand written descriptor for the scipy module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return (build_setuptools(), 
            build_distutils(), 
            build_zipfile(),
            build_dummy_threading(),
            )

def build_setuptools(des = None):
    if des is None:
        des = ModuleDescriptor('setuptools')
    des.add_module('setuptools')
    
    # 
    des.add_dependency('ctypes')
    des.add_dependency('distutils')
    des.add_dependency('configparser')
    des.add_dependency('shutil')
    return des

def build_distutils(des = None):
    if des is None:
        des = ModuleDescriptor('distutils')
    des.add_module('distutils')
    
    return des

def build_zipfile(des = None):
    if des is None:
        des = ModuleDescriptor('zipfile')
    des.add_module('zipfile')
    
    return des  

def build_dummy_threading(des = None):
    if des is None:
        des = ModuleDescriptor('dummy_threading')
    des.add_module('dummy_threading')
    
    des.add_dependency('socket')
    return des  