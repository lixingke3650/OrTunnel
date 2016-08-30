#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: TunnelService.py

# std
import queue

# original
from Tool import *
import globals
from Client.ListenService import *
from Client.PostService import *

__all__ = ['TunnelService']

class TunnelService():
    """TunnelService
    服务入口"""

    # 隧道队列
    _TunnelQueue = None
    # 监听服务
    _ListenService = None
    # 送信服务
    _PostService = None

    def __init__(self, maxdata = 128):
        '''隧道服务初始化
        maxdata: 最大隧道条数(本地监听最大响应数)'''

        self._TunnelQueue = queue.Queue(maxsize = maxdata)
        self._ListenService = ListenService(globals.G_LISTEN_HOST, globals.G_LISTEN_PORT, self._TunnelQueue, globals.G_LISTEN_CONNECT_MAXNUMBER)
        self._PostService = PostService(globals.G_TARGET_HOST, globals.G_TARGET_PORT, self._TunnelQueue)

    def start(self):
        ret = True
        if (self._ListenService.start() != True):
            ret = False
            globals.G_Log.error( 'Listen Service Start error! [TunnelService.py:TunnelService:start]' )
        elif (self._PostService.start() != True):
            ret = False
            globals.G_Log.error( 'Post Service Start error! [TunnelService.py:TunnelService:start]' )
        if (ret != True):
            self._ListenService.stop()
            self._PostService.stop()

        return ret

    def testing(self):
        '''服务测试
        '''

        if (self._PostService.testing() != True):
            globals.G_Log.info( 'Post Service Testing fail! [TunnelService.py:TunnelService:testing]' )
            IO.printX('tunnel test : NG.')
            return False
        IO.printX('tunnel test : OK.')
        return True
