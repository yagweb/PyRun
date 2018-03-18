# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 00:09:41 2018

@author: yagweb
"""
import os
import sys

def get_method(pyver):
    method = {
        '35': add_py36,
        '36': add_py36
    }.get(pyver, None)
    return 'matplotlib', method

def add_py36(bundler, dependency):
    bundler.add_module('matplotlib')
    
    dependency.add_module('six')
    dependency.add_module('distutils')
    dependency.add_module('inspect')
    dependency.add_module('ast')
    dependency.add_module('dis')
    dependency.add_module('opcode')
    dependency.add_module('glob')
    dependency.add_module('gzip')
    dependency.add_module('_compression')
    dependency.add_module('subprocess')
    dependency.add_module('pyparsing')
    dependency.add_module('cycler')
    dependency.add_module('urllib')
    dependency.add_module('base64')
    dependency.add_module('email')
    dependency.add_module('http')
    dependency.add_module('quopri')
    dependency.add_module('calendar')
    dependency.add_module('uu')
    dependency.add_module('nturl2path')
    dependency.add_module('json')
    dependency.add_module('dateutil')
    dependency.add_module('csv')
    dependency.add_module('unicodedata')
    
    mkldir = os.path.join(sys.prefix, 'Library/bin/mkl_avx2.dll')
    bundler.add_path(mkldir)