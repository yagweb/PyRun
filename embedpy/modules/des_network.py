'''
hand written descriptor for the platform module
'''
from .descriptor import ModuleDescriptor


def get_descriptors():
    return [build_requests(),]


def build_requests(des = None):
    if des is None:
        des = ModuleDescriptor('requests')
    des.add_module('requests')

    des.add_dependency('idna')
    des.add_dependency('certifi')
    des.add_dependency('cgi')
    des.add_dependency('chardet')
    des.add_dependency('hmac')
    des.add_dependency('urllib3')
    des.add_dependency('requests')
    return des