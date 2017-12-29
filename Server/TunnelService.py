#! 
# -*-coding: utf-8-*-
# FileName: TunnelService.py

# std
import queue

# original
from Tool import *
import globals
import Server


__all__ = ['TunnelService']

class TunnelService():
    ''''''

    # tunnel group list
    _TunnelGroupList = None
    # tunnel worker queue
    _TunnelWorkerQueue = None
    # listen service
    _ListenService = None
    # data post service
    _PostService = None

    def __init__(self, maxdata = 128):
        ''''''

        self._TunnelGroupList = []
        self._TunnelWorkerQueue = queue.Queue(maxsize = maxdata)
        if (globals.G_TUNNEL_METHOD == 'UDP'):
            self._ListenService = Server.Udp.ListenService(self._TunnelGroupList, self._TunnelWorkerQueue)
            self._PostService = Server.Udp.PostService(self._TunnelGroupList, self._TunnelWorkerQueue)
        elif (globals.G_TUNNEL_METHOD == 'TCP'):
            self._ListenService = Server.Tcp.ListenService(self._TunnelGroupList, self._TunnelWorkerQueue)
            self._PostService = Server.Tcp.PostService(self._TunnelGroupList, self._TunnelWorkerQueue)

    def start(self):
        ''''''

        if (self._ListenService == None):
            return False
        if (self._PostService == None):
            return False
        ret = True
        if (self._ListenService.start() != True):
            ret = False
            globals.G_Log.error('Listen Service Start error! [TunnelService.py:TunnelService:start]')
        elif (self._PostService.start() != True):
            ret = False
            globals.G_Log.error('Post Service Start error! [TunnelService.py:TunnelService:start]')
        if (ret != True):
            self._ListenService.stop()
            self._PostService.stop()

        return ret
