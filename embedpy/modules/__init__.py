#
import os
from .descriptor import ModuleDescriptor
from warnings import warn

descriptors = []

for file in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(file)
    if ext == ".py" and name.startswith("des_"):
        _tmp_ = __import__('embedpy.modules.' + name, fromlist = ['get_descriptor'])
        try:
            des = _tmp_.get_descriptors()
            descriptors.extend(des)
        except Exception as ex:
            warn(f">> register module failed '{name}', {str(ex)}")