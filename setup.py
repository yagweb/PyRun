
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension
    
console = Extension("embedpy.bases.console", 
        ["embedpy/source/console.c"],
        depends = [], 
        libraries = [])
extensions = [console]

setup(name = "embedpy",
        description = "embed python or pack python",
        long_description = "bundle python scripts for embedded use or create standalone executables from Python scripts",
        version = "6.0b1",
        ext_modules = extensions,
        packages = ['embedpy'],
        maintainer="Wenguang Yang",
        maintainer_email="hbtmdxywg@126.com",
        url = "https://github.com/yagweb/PyRun",
        keywords = "freeze",
        license = "Python Software Foundation License")