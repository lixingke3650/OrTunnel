# !usr/bin/python
# -*- coding: utf-8 -*-
# Filename: logger.py

# log level:
# logging.CRITICAL # 50
# logging.ERROR    # 40
# logging.WARN     # 30
# logging.WARNING  # 30
# logging.INFO     # 20
# logging.DEBUG    # 10
# logging.NOTSET   # 0

# std
import os
import logging
import inspect


__all__ = ["OrLog", "getLogger"]

_Logger = None

class OrLog(object):
    _Logger = None
    _LogHandler = None
    _LogFormat = None

    def __init__(self, name, tab='orlog'):
        # logger实例获取
        self._Logger = logging.getLogger(name)
        # 指定logger控制器
        self._LogHandler = logging.FileHandler(filename=name + '.log')
        # 设置log格式
        # self._LogFormat = logging.Formatter('%(levelname)-9s %(asctime)s  %(filename)s[line:%(lineno)d]  %(message)s')
        self._LogFormat = logging.Formatter('%(levelname)-9s %(asctime)s [' + tab + ']%(message)s')
        # 格式信息加载到控制器上
        self._LogHandler.setFormatter(self._LogFormat)
        # 激活控制器信息
        self._Logger.addHandler(self._LogHandler)
        # 设置log级别
        self._Logger.setLevel(logging.DEBUG)

    def setLevel(self, level):
        if (level == 'CRITICAL'):
            self._Logger.setLevel(logging.CRITICAL)
        elif (level == 'ERROR'):
            self._Logger.setLevel(logging.ERROR)
        elif (level == 'WARN'):
            self._Logger.setLevel(logging.WARN)
        elif (level == 'INFO'):
            self._Logger.setLevel(logging.INFO)
        elif (level == 'DEBUG'):
            self._Logger.setLevel(logging.DEBUG)
        else:
            self._Logger.setLevel(logging.NOTSET)

    def getLevel(self):
        return logging.getLevelName(self._Logger.getEffectiveLevel())

    def debug(self, msg):
        self._Logger.debug(self.reframe(msg))

    def info(self, msg):
        self._Logger.info(self.reframe(msg))

    def warn(self, msg):
        self._Logger.warn(self.reframe(msg))

    def error(self, msg):
        self._Logger.error(self.reframe(msg))

    def critical(self, msg):
        self._Logger.critical(self.reframe(msg))

    def reframe(self, msg):
        callerframerecord = inspect.stack()[2]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        # str.join
        # return ':'.join([os.path.basename(info.filename), info.function, str(info.lineno), msg])
        # format
        return "{}:{}:{}: {}".format(os.path.basename(info.filename), info.function, info.lineno, msg)
        # f-string, after python 3.6.2
        # return f'{os.path.basename(info.filename)}:{info.function}:{info.lineno}: {msg}'

def getLogger(name='log', tab=''):
    global _Logger
    if( _Logger == None ):
        _Logger  = OrLog(name, tab)

    return _Logger

# if __name__ == "__main__":
#   getLogger()
#   _Logger.debug("hello")