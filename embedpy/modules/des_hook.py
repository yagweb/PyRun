'''
hand written descriptor for the hook module
'''
import os
from .descriptor import ModuleDescriptor


def get_descriptors():
    return build_hook(), build_update()


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


def build_update(des = None):
    if des is None:
        des = ModuleDescriptor('update_helper')
    des.add_path(os.path.join(__file__, "../../update_helper.py"))
    des.add_module('shutil')
    for name in ['re', 'sre_constants', 'traceback', 
                 'tokenize', 'bz2', 'threading', 
                 '_sre', 'posixpath', 'zlib', 
                 'fnmatch', 'enum', 'copyreg', 
                 'lzma', '_bz2', '_compression', 
                 'linecache', 'sre_compile', 'time', 
                 'token', '_lzma', 'sre_parse']:
        des.add_module(name)
    return des