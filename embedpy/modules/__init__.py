#
import os
from .descriptor import ModuleDescriptor
from ..logger import logger

descriptors = []

for file in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(file)
    if ext == ".py" and name.startswith("des_"):
        _tmp_ = __import__('embedpy.modules.' + name, fromlist = ['get_descriptors'])
        try:
            des = _tmp_.get_descriptors()
        except Exception as ex:
            logger.error(f">> register module failed '{name}', {str(ex)}")
            continue
        descriptors.extend(des)