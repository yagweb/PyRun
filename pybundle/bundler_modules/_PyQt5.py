# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 00:09:27 2018

@author: yagweb
"""
import os
import sys
import glob

def get_method(pyver):
    method = {
        '35': add_py36,
        '36': add_py36
    }.get(pyver, None)
    return 'PyQt5', method

def add_py36(bundler, dependency):
    bundler.add_module('PyQt5', ignore = ['port_v2'])
    
    for name in ['Qt5Core', 'Qt5Gui', 'Qt5Widgets']:
        bundler.add_path(os.path.join(sys.prefix, 'Library/bin/%s.dll' % name))
    
    # fixed: could not find or load the Qt platform plugin "windows"
    # need to copy with folder and put as the same level with the exe
    if sys.platform == 'win32':
        bundler.add_path(os.path.join(sys.prefix, 'Library/plugins/platforms/qwindows.dll'), '../platforms')
        
    #
    dependency.add_module('sip')
    
def add_all_dlls(bundler):
    # run the program, then delete all the dlls, then the skipped dll is the minimuns
    bin_dir = os.path.join(sys.prefix, 'Library/bin/')
    for dll in glob.glob(bin_dir + "Qt5*"):
        if '~' in dll:
            continue
        bundler.add_path(dll)