# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 23:18:07 2018

@author: yagweb
"""
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('socket'))

def build(des):
    des.add_module('sqlite3', ignore = ['test'])
    des.add_module('_sqlite3')
    des.add_dll_in_library_bin('sqlite3')
    
    #
    des.add_dependency('datetime')
    return des