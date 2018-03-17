# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 23:46:44 2018

@author: yagweb
"""
import os
import sys

def get_method(pyver):
    method = {
        '35': add_numpy_py35,
        '36': add_numpy_py36
    }.get(pyver, None)
    return 'numpy', method

def add_numpy_py36(bundler, dependency):
    bundler.add_module('numpy',
                       ignore = ['doc',
                                 'f2py', 'testing', 'tests'])
    #Windows Anaconda
    mkldir = os.path.join(sys.prefix, 'Library/bin')
    #WinPython
    #import numpy
    #mkldir = os.path.join(sys.prefix, os.path.join(numpy.__file__, "../core"))
    for mkl in ('libiomp5md', 'mkl_avx2', 'mkl_core', 'mkl_intel_thread', 'mkl_rt'):
        dependency.add_path(mkldir + os.path.sep + mkl+'.dll')
    dependency.add_module('__future__')
    dependency.add_module('warnings')
    
def add_numpy_py35(bundler, dependency):
    '''
    not working, because the 'multiarray' module
    '''
    bundler.add_module('numpy')
    #Windows Anaconda
    mkldir = os.path.join(sys.prefix, 'Library/bin')
    #WinPython
    #import numpy
    #mkldir = os.path.join(sys.prefix, os.path.join(numpy.__file__, "../core"))
    for mkl in ('libiomp5md', 'mkl_avx2', 'mkl_core', 'mkl_intel_thread', 'mkl_rt'):
        dependency.add_path(mkldir + os.path.sep + mkl+'.dll')
    dependency.add_module('__future__')
    dependency.add_module('warnings')
