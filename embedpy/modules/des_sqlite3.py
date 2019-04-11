'''
hand written descriptor for the sqlite3 module
'''
import os
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_sqlite3(), 

def build_sqlite3(des = None):
    if des is None:
        des = ModuleDescriptor('sqlite3')
    des.add_module('sqlite3', ignore = ['test'])
    des.add_module('_sqlite3')
    des.add_dll('sqlite3')
    import _sqlite3
    des.add_dll_search_path(os.path.dirname(_sqlite3.__file__))
    
    #
    des.add_dependency('datetime')
    return des