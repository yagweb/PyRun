# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 23:46:44 2018

@author: yagweb
"""
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('numpy'))

def build(des):
    des.add_module('numpy', ignore = ['doc',
                                 'f2py', 
#                                 'tests'
                                 ])
    #Windows Anaconda
    des.add_dlls_in_library_bin(('libiomp5md', 'mkl_core', 'mkl_intel_thread'))
    
    # 
    des.add_dependency('ctypes')
    # the 'multiarray' module needs sqlite3 and socket
    des.add_dependency('socket')
    des.add_dependency('sqlite3')
    des.add_dependency('__future__')
    des.add_dependency('warnings')
    des.add_dependency('unittest')
    des.add_dependency('difflib')
    des.add_dependency('logging')
    des.add_dependency('string')
    des.add_dependency('pprint')
    des.add_dependency('fnmatch')
    des.add_dependency('posixpath')
    des.add_dependency('argparse')
    des.add_dependency('copy')
    des.add_dependency('textwrap')
    des.add_dependency('gettext')
    des.add_dependency('signal')
    des.add_dependency('shutil')
    des.add_dependency('tempfile')
    des.add_dependency('random')
    des.add_dependency('hashlib')
    des.add_dependency('bisect')
    des.add_dependency('dummy_threading')
    des.add_dependency('_dummy_thread')
    des.add_dependency('threading')
    return des
    