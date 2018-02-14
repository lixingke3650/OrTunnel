#!
# -*-coding: utf-8-*-
# FileName: TunnelService.py

# std
import queue
import threading

# original
from Tool import *
import globals
import Client


__all__ = ['TunnelService']

class TunnelService():
    """"""

    # tunnel group list
    _TunnelGroupList = None
    # tunnel worker queue
    _TunnelWorkerQueue = None
    # tunnel worker list
    _TunnelWorkerList = None
    # listen service
    _ListenService = None
    # data post service
    _PostService = None
    # thread lock
    _TunnelWorkThreadRLock = None

    def __init__(self, maxdata = 128):
        ''''''

        self._TunnelGroupList = []
        self._TunnelWorkerList = []
        self._TunnelWorkerQueue = queue.Queue(maxsize = maxdata)
        self._TunnelWorkThreadRLock = threading.RLock()

        self._ListenService = Client.ListenService(self._TunnelGroupList, self._TunnelWorkerQueue, self.tunnelworksmanager)
        self._PostService = Client.PostService(self._TunnelGroupList, self._TunnelWorkerQueue, self.tunnelworksmanager)

    def start(self):
        ''''''

        if (self._ListenService == None):
            return False
        if (self._PostService == None):
            return False
        ret = True
        if (self._ListenService.start() != True):
            ret = False
            globals.G_Log.error('Listen Service Start error! [TunnelService.py:start]')
        elif (self._PostService.start() != True):
            ret = False
            globals.G_Log.error('Post Service Start error! [TunnelService.py:start]')
        if (ret != True):
            self._ListenService.stop()
            self._PostService.stop()

        return ret

    def testing(self):
        ''''''
        return 'dummy OK. (testing)'

    def tunnelworksmanager(self, oper, tunnelworker = None):
        '''proxyworks add and del.
        oper: add/del/get'''

        # return work count
        ret = 0
        # thread lock
        self._TunnelWorkThreadRLock.acquire()
        try:
            if (oper == 'add'):
                if ((tunnelworker in self._TunnelWorkerList) == False):
                    self._TunnelWorkerList.append(tunnelworker)
                    ret = len(self._TunnelWorkerList)
                    if (globals.G_LOG_LEVEL == 'DEBUG'):
                        IO.printX('worker %s (count %d)' %(oper, ret))
            elif (oper == 'del'):
                if ((tunnelworker in self._TunnelWorkerList) == True):
                    self._TunnelWorkerList.remove(tunnelworker)
                    ret = len(self._TunnelWorkerList)
                    if (globals.G_LOG_LEVEL == 'DEBUG'):
                        IO.printX('worker %s (count %d)' %(oper, ret))
            elif (oper == 'get'):
                ret = self._TunnelWorkerList

        except Exception as e:
            globals.G_Log.error( 'tunnelworks add or del error! [TunnelServer.py:tunnelworksmanager] --> %s' %e )
        # thread unlock
        self._TunnelWorkThreadRLock.release()
        # return work count
        return ret;