'''
hand written descriptor for the pythonnet module
'''
import os
import sys
from .descriptor import ModuleDescriptor


def get_descriptors():
    return [build_pythonnet(), ]


def build_pythonnet(des = None):
    if des is None:
        des = ModuleDescriptor('pythonnet')
    des.add_module('clr')
    des.add_dependency('platform')
    des.add_dependency('signal')
    
    import clr
    module_path = clr.__file__ if os.path.exists(clr.__file__) else clr.__spec__.origin
    path = os.path.join(os.path.dirname(module_path), "Python.Runtime.dll")
    # dll should be put beside the pyd file
    # 2.4.0 has a bug: System.AccessViolationException: Attempted to read or write protected memory.
    des.add_path(path, dest="extensions/Python.Runtime.dll")
    return des
