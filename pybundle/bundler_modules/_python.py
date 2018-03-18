# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 23:54:26 2018

@author: yagweb
"""
from .module_descriptor import ModuleDescriptor

def get_descriptor():
    return build(ModuleDescriptor('python'))

def build(des):
    des.add_module('encodings')
    des.add_module('collections')
    des.add_module('traceback')
    des.add_module('copyreg')
    des.add_module('abc')
    des.add_module('types')
    des.add_module('locale')
    des.add_module('functools')
    des.add_module('sre_constants')
    des.add_module('sre_parse')
    des.add_module('_bootlocale')
    des.add_module('linecache')
    des.add_module('_collections_abc')
    des.add_module('_weakrefset')
    des.add_module('reprlib')
    des.add_module('operator')
    des.add_module('heapq')
    des.add_module('io')
    des.add_module('re')
    des.add_module('sre_compile')
    des.add_module('weakref')
    des.add_module('keyword')
    des.add_module('codecs')
    #site, may not need when Py_NoSiteFlag = 1?
    des.add_module('site')
    des.add_module('_sitebuiltins')
    des.add_module('os')
    des.add_module('stat')
    des.add_module('ntpath')
    des.add_module('genericpath')
    des.add_module('sysconfig')
    return des