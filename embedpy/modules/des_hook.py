'''
hand written descriptor for the hook module
'''
import os
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_hook(), 

def build_hook(des = None):
    if des is None:
        des = ModuleDescriptor('hook')
    des.add_path(os.path.join(__file__, "../../hook.py"))
    des.add_module("imp")
    des.add_module("importlib")
    des.add_module("contextlib")
    des.add_module("tokenize")
    des.add_module('token')
    des.add_module('enum')
    des.add_module('warnings')
    des.add_module('numbers')
    des.add_module('pickle')  
    des.add_module('_compat_pickle')
    return des