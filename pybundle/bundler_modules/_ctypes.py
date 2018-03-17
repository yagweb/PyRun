# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 09:12:49 2018

@author: yagweb
"""

def get_method(pyver):
    return 'ctypes', add_ctypes

def add_ctypes(bundler, dependency):
    bundler.add_module('ctypes')
    bundler.add_module('_ctypes')
    dependency.add_module('struct')