# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 23:18:07 2018

@author: yagweb
"""
import os

def get_method(pyver):
    return 'sqlite3', add_sqlite3
 
def add_sqlite3(bundler, dependency):
    import sqlite3
    bundler.add_module('sqlite3', ignore = ['test'])
    bundler.add_module('_sqlite3')
    bundler.add_path(os.path.join(sqlite3.__file__, '../../../DLLs/sqlite3.dll'))
    dependency.add_module('datetime')