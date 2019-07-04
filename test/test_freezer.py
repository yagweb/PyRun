# -*- coding: utf-8 -*-
# In order to test the freezer output, the Anaconda3 folder should be renamed, so dll's can
# only be searched in the freezed program.

# if dll missing error occurs, copy all the dll into the DLLs, run the program, while
# keep the program running, delete all the dll files and the dependency dlls will be kept.
# Then, modify its descriptor file according to its dependencies.

import os
import sys
from embedpy.freezer import Freezer


def freeze_test(dest_path):
    sys.argv.append('build')
    print('build start.')
    fr = Freezer(dest_path)
    fr['python'].is_compress = True
    fr.add_package('ctypes', is_compress = True)
    fr.add_exe(os.path.join(cur_dir, "main/test_ctypes.py"), 
        name="test", 
        is_source=True,
        init_script=os.path.join(cur_dir, "main/init_script.py"))
    fr.add_update_exe()
    fr.build()
    print('build end.')


if __name__ == '__main__':
    cur_dir = os.path.dirname(__file__)
    dest_path = os.path.join(cur_dir, '../bin/demo')
    freeze_test(dest_path)
