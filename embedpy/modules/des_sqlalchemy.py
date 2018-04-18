'''
hand written descriptor for the sqlalchemy module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_sqlalchemy(), 

def build_sqlalchemy(des = None):
    if des is None:
        des = ModuleDescriptor('sqlalchemy')
    des.is_compressable = False
    des.add_module('sqlalchemy')
    
    des.add_dependency('configparser')
    des.add_dependency('json')
    des.add_dependency('decimal')
    return des