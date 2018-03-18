# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 10:19:26 2018

@author: yagweb
"""
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('socket'))

def build(des):
    des.add_module('socket')
    des.add_module('_socket')
    des.add_module('select') #pyd
    #
    des.add_dependency('selectors')
    des.add_dependency('enum')
    des.add_dependency('tokenize')
    des.add_dependency('token')
    return des