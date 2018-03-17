# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 23:54:26 2018

@author: yagweb
"""

def bundle_python(bundler):
    bundle_python_35(bundler)
    return bundler
     
def bundle_python_35(bundler : 'Bundler'):
    bundler.add_module('encodings')
    bundler.add_module('collections')
    bundler.add_module('traceback')
    bundler.add_module('copyreg')
    bundler.add_module('abc')
    bundler.add_module('types')
    bundler.add_module('locale')
    bundler.add_module('functools')
    bundler.add_module('sre_constants')
    bundler.add_module('sre_parse')
    bundler.add_module('_bootlocale')
    bundler.add_module('linecache')
    bundler.add_module('_collections_abc')
    bundler.add_module('_weakrefset')
    bundler.add_module('reprlib')
    bundler.add_module('operator')
    bundler.add_module('heapq')
    bundler.add_module('io')
    bundler.add_module('re')
    bundler.add_module('sre_compile')
    bundler.add_module('weakref')
    bundler.add_module('keyword')
    bundler.add_module('codecs')
    #site, may not need when Py_NoSiteFlag = 1?
    bundler.add_module('site')
    bundler.add_module('_sitebuiltins')
    bundler.add_module('os')
    bundler.add_module('stat')
    bundler.add_module('ntpath')
    bundler.add_module('genericpath')
    bundler.add_module('sysconfig')
    return bundler