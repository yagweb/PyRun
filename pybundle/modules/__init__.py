#
import os
from .descriptor import ModuleDescriptor

descriptors = []

for file in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(file)
    if ext == ".py" and name.startswith("des_"):
        _tmp_ = __import__('pybundle.modules.' + name, fromlist = ['get_descriptor'])
        des = _tmp_.get_descriptors()
        descriptors.extend(des)