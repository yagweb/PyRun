import os
import sys


def get_main_module(path_builder):
    print(f"__init__ script is called, {path_builder.root}, {sys.argv}")
    return "__main__test"


def on_error(loader, ex, traceback):
    print("on_error from the init module")
    with open(os.path.join(sys.prefix, 'error_init.txt'), 'w') as fp:
        fp.write(str(sys.executable))
        fp.write("\n")
        fp.write(str(sys.prefix))
        fp.write("\n")
        fp.write(str(sys.path))
        fp.write("\n")
        fp.write(f"{str(ex)}\n")
        traceback.print_exc(file=fp)