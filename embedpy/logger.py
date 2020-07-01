import sys
import logging
from logging import Logger
# ref https://www.cnblogs.com/telecomshy/p/10630888.html
# set basicConfig will add a default handler (sys.stderr) to the root logger
# logging.basicConfig(level = logging.WARN, 
#                    format = '%(asctime)s - %(levelname)s - %(message)s')
# logging.getLogger().handlers.clear()


class LoggerHelper:
    _loggers = {}
    default_level = logging.INFO
    
    def __new__(cls, name):
        if name in cls._loggers:
            return cls._loggers[name]
        cls._loggers[name] = self = super().__new__(cls)
        self.name = name
        # logging.getLogger() cannot be removed
        self.logger = Logger(name)
        self.logger.setLevel(logging.DEBUG)
        self.handlers = {}
        return self

    def dispose(self):
        if self.name in LoggerHelper._loggers:
            del LoggerHelper._loggers[self.name]

    @classmethod
    def get(cls, name):
        obj = LoggerHelper._loggers.get(name)
        if obj is None:
            raise Exception(f"logger {name} not exist")
        return obj

    def setLevel(self, level):
        self.logger.setLevel(level)

    def add_handler(self, name, handler):
        ''' If the handler level is large than the logger level, it will never be called.
        '''
        if name in self.handlers:
            self.logger.removeHandler(self.handlers[name])
        self.logger.addHandler(handler)
        self.handlers[name] = handler

    def remove_handler(self, name):
        self.logger.removeHandler(self.handlers[name])
        del self.handlers[name]

    def add_file_handler(self, name, file_path, mode='a', fstr=None, 
                         level=None):
        if fstr is None:
            fstr = '%(asctime)s - %(levelname)s - %(message)s'
        if level is None:
            level = LoggerHelper.default_level
        fh = logging.FileHandler(filename=file_path, mode=mode, encoding = 'utf-8')
        fh.setLevel(level)
        formatter = logging.Formatter(fstr)
        fh.setFormatter(formatter)
        self.add_handler(name, fh)
    
    def add_stream_handler(self, name="default", stream=sys.stderr, 
                           fstr=None, level=None):
        if fstr is None:
            fstr = '%(asctime)s - %(levelname)s - %(message)s'
        if level is None:
            level = LoggerHelper.default_level
        fh = logging.StreamHandler(stream)
        fh.setLevel(level)
        formatter = logging.Formatter(fstr)
        fh.setFormatter(formatter)
        self.add_handler(name, fh)


logger_helper = LoggerHelper("embedpy")
logger = logger_helper.logger
logger_helper.add_stream_handler(level=logging.INFO)