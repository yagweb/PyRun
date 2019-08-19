'''
hand written descriptor for the numy module
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_numpy(), 

def build_numpy(des = None):
    if des is None:
        des = ModuleDescriptor('numpy')
    des.is_compressable = False
    des.add_module('numpy', ignore = ['doc',
                                 'f2py', 
                                 'tests'
                                 ])
    des.add_dlls(('libiomp5md', 'mkl_core', 'mkl_intel_thread'))
    # size 50M, seems intel doesnot need this, donnot know when need
    des.add_dlls(('mkl_rt', 'mkl_def'))
    
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
    des.add_dependency('platform')
    return des
    