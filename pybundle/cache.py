
class ItemCache(object):
    '''
    shared by multiple Bundlers
    '''
    def __init__(self):
        self.modules = {}
        
    def skip_module(self, name, owner = None):
        if name in self.modules:
            return
        self.modules[name] = owner
        
    def skip_modules(self, names, owner = None):        
        for name in names:
            if name in self.modules:
                continue
            self.modules[name] = owner    
        
    def add_module(self, name, owner):
        _owner = self.modules.get(name, None)
        if _owner is not None:
#            if _owner == name:
#                return None
            return _owner
        self.modules[name] = owner
        return None

class ModuleCache(ItemCache):
    def __init__(self):
        super(ModuleCache, self).__init__()
        # modules in the python dll, has not __file__ attr
        self.skip_modules(['itertools', 'sys',
                             'builtins', 'time',
                             '_ast', '_struct', '_signal',
                             'zlib', '_datetime', '_functools',
                             '_imp', 'math', 'atexit', '_random',
                             '_pickle', '_blake2', '_stat','binascii',
                             '_sha512', '_sha256', 'tty',
                             '_io','winreg','_heapq','_operator',
                             'errno','_opcode','_tracemalloc',
                             '_bisect',
                             'nt','_winapi', '_sha3', '_weakref',
                             '_string', '_warnings',
                             '_md5', 'msvcrt',
                             '_collections','_sha1','_sre','_thread','marshal',
                             '_codecs', 'zipimport', '_locale','gc'],
            owner = 'buildins')
        