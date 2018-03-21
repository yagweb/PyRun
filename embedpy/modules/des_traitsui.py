'''
hand written descriptor for the traitsui module
traits, pyface
'''
from .descriptor import ModuleDescriptor

def get_descriptors():
    return build_traits(), build_pyface(), build_traitsui(),

def build_traitsui(des = None):
    if des is None:
        des = ModuleDescriptor('traitsui')
    des.add_module('traitsui')
    
    # 
    des.add_dependency('pyface')
    des.add_dependency('traits')
    
    des.add_dependency('uuid')
    des.add_dependency('shelve')
    des.add_dependency('pkg_resources')
    des.add_dependency('zipfile')
    des.add_dependency('plistlib')
    des.add_dependency('xml')
    des.add_dependency('pyexpat')
    
    des.add_dependency('cgi')
    des.add_dependency('html')
    return des

def build_pyface(des = None):
    if des is None:
        des = ModuleDescriptor('pyface')
    des.add_module('pyface')
        
    # need the entry_points.txt in egg-info folder for pkg_resources.iter_entry_points
    # reqirements.txt should be removed, because pip is need to check
    des.add_egg_info_files(['entry_points.txt'])
    
    # 
    des.add_dependency('PyQt5')    
    return des

def build_traits(des = None):
    if des is None:
        des = ModuleDescriptor('traits')
    des.add_module('traits') #egg-info
    return des
