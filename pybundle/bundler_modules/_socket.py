# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 10:19:26 2018

@author: yagweb
"""

def get_method(pyver):
    return 'socket', add_socket
 
def add_socket(bundler, dependency):
    bundler.add_module('socket')
    bundler.add_module('_socket')
    bundler.add_module('select') #pyd
    dependency.add_module('selectors')
    dependency.add_module('enum')
    dependency.add_module('tokenize')
    dependency.add_module('token')