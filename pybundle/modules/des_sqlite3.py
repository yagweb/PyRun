'''
hand written descriptor for the sqlite3 module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_sqlite3(), 

def build_sqlite3(des = None):
    if des is None:
        des = ModuleDescriptor('sqlite3')
    des.add_module('sqlite3', ignore = ['test'])
    des.add_module('_sqlite3')
    des.add_dll_in_DLLs('sqlite3')
    
    #
    des.add_dependency('datetime')
    return des