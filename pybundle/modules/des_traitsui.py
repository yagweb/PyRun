'''
hand written descriptor for the traitsui module
traits, pyface
'''

from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_traitsui() ,

def build_traitsui(des = None):
    if des is None:
        des = ModuleDescriptor('traitsui')
    des.add_module('traits')
    des.add_module('pyface')
    des.add_module('traitsui')
    
    # 
    des.add_dependency('PyQt5')
    return des
