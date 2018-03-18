'''
hand written descriptor for the socket module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_socket(), 

def build_socket(des = None):
    if des is None:
        des = ModuleDescriptor('socket')
    des.add_module('socket')
    des.add_module('_socket')
    des.add_module('select') #pyd
    #
    des.add_dependency('selectors')
    des.add_dependency('enum')
    des.add_dependency('tokenize')
    des.add_dependency('token')
    return des