import sys

def get_main_module(path_builder):
    print(f"__init__ script is called, {path_builder.root}, {sys.argv}")
    return "__main__test"