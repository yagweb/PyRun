# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 00:09:41 2018

@author: yagweb
"""
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('matplotlib'))

def build(des):
    des.add_module('matplotlib')
    
    des.add_dependency('six')
    des.add_dependency('distutils')
    des.add_dependency('inspect')
    des.add_dependency('ast')
    des.add_dependency('dis')
    des.add_dependency('opcode')
    des.add_dependency('glob')
    des.add_dependency('gzip')
    des.add_dependency('_compression')
    des.add_dependency('subprocess')
    des.add_dependency('pyparsing')
    des.add_dependency('cycler')
    des.add_dependency('urllib')
    des.add_dependency('base64')
    des.add_dependency('email')
    des.add_dependency('http')
    des.add_dependency('quopri')
    des.add_dependency('calendar')
    des.add_dependency('uu')
    des.add_dependency('nturl2path')
    des.add_dependency('json')
    des.add_dependency('dateutil')
    des.add_dependency('csv')
    des.add_dependency('unicodedata')
    
    des.add_dll_in_library_bin('mkl_avx2')
    return des