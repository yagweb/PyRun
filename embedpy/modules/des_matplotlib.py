'''
hand written descriptor for the matplotlib module
'''
import platform
from .descriptor import ModuleDescriptor
from distutils.version import StrictVersion

def get_descriptors():
    return build_matplotlib(), build_decimal()

def build_matplotlib(des = None):
    if des is None:
        des = ModuleDescriptor('matplotlib')
    des.is_compressable = False
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
    des.add_dependency('http')
    des.add_dependency('quopri')
    des.add_dependency('calendar')
    des.add_dependency('uu')
    des.add_dependency('nturl2path')
    des.add_dependency('json')
    des.add_dependency('dateutil')
    des.add_dependency('csv')
    des.add_dependency('unicodedata')
    des.add_dependency('decimal')
    des.add_dependency('distutils')
    
    des.add_dll('mkl_avx2')
    des.add_dll('mkl_def')
    if StrictVersion(platform.python_version()) > StrictVersion('3.6.1'):
        des.add_dll('freetype')
    des.add_dll('libifcoremd')
    des.add_dll('libmmd')
    des.add_dll('libpng16')
    des.add_dll('zlib')
    return des

def build_decimal(des = None):
    if des is None:
        des = ModuleDescriptor('decimal')
    des.add_module('decimal')
    
    des.add_dependency('_pydecimal')
    des.add_dependency('_decimal')
    des.add_dependency('dummy_threading')
#    des.add_dependency('socket')
    return des