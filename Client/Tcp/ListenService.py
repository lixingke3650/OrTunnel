#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: ListenService.py

# std
import socket
import threading
import queue

# original
from Tool import *
import globals
from Client.Tcp.TunnelWorker import *

__all__ = ['ListenService']

class ListenService():
    """ListenService服务
    监听本地连接，并读取数据存放到队列中"""

    _TunnelWorkerQueue = None
    _ServiceSocket = None
    _ServerAddress = None
    _TunnelGroupNumber = None
    _TunnelGroupInfo = None
    _TunnelGroupList = None
    _tunnelWorksManager = None
    _isRun = None

    def __init__(self, tunnelgrouplist, tunnelworkerqueue, tunnelworksmanager):
        '''监听服务初始化'''
        if (globals.G_TUNNEL_NUM > len(globals.G_TUNNEL_GROUP_INFO)):
            self._TunnelGroupNumber = len(globals.G_TUNNEL_GROUP_INFO)
        else:
            self._TunnelGroupNumber = globals.G_TUNNEL_NUM
        self._TunnelGroupInfo = globals.G_TUNNEL_GROUP_INFO
        self._TunnelGroupList = tunnelgrouplist
        self._TunnelWorkerQueue = tunnelworkerqueue
        self._tunnelWorksManager = tunnelworksmanager
        self._isRun = False

    def start(self):
        '''监听服务启动'''
        if (self._TunnelWorkerQueue == None):
            return False

        try:
            globals.G_Log.debug('Listen Service Start.')
            for i in range(self._TunnelGroupNumber):
                globals.G_Log.debug('Listen Service Start Start. %d' %i)
                globals.G_Log.debug('Listen Service Start Start. %d' %self._TunnelGroupNumber)
                tunnelgroupinfo = self._TunnelGroupInfo[i]
                listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address = (tunnelgroupinfo[globals.GD_LISTENIP], tunnelgroupinfo[globals.GD_LISTENPORT])
                listen_socket.bind(address)
                listen_socket.listen(globals.G_LISTEN_CONNECT_HOLDMAX)
                tunnelgroup = TunnelGroup()
                tunnelgroup._Listen_Socket = listen_socket
                tunnelgroup._ListenIP = tunnelgroupinfo[globals.GD_LISTENIP]
                tunnelgroup._ListenPort = tunnelgroupinfo[globals.GD_LISTENPORT]
                tunnelgroup._TargetIP = tunnelgroupinfo[globals.GD_TARGETIP]
                tunnelgroup._TargetPort = tunnelgroupinfo[globals.GD_TARGETPORT]
                generatorThread = threading.Thread(target = self.generator, args = (tunnelgroup,))
                # generatorThread.daemon = True
                tunnelgroup._GeneratorThread = generatorThread
                self._TunnelGroupList.append(tunnelgroup)
            self._isRun = True
            for j in range(len(self._TunnelGroupList)):
                self._TunnelGroupList[j]._GeneratorThread.start()
            globals.G_Log.debug('Listen Service Start End.')
            return True
        except Exception as e:
            globals.G_Log.error('Listen Service Start error! [ListenService.py:start] --> %s' %e)

    def stop(self):
        '''监听服务停止'''
        if (self._isRun == False):
            return True
        try:
            globals.G_Log.debug('Listen Service Stop Start.')
            self._isRun = False
            for j in range(len(self._TunnelGroupList)):
                self._TunnelGroupList[j]._Listen_Socket.shutdown(socket.SHUT_RDWR)
                self._TunnelGroupList[j]._Listen_Socket.close()
                self._TunnelGroupList[j]._GeneratorThread.jion(10)
            globals.G_Log.debug('Listen Service Stop End.')
            return True
        except Exception as e:
            globals.G_Log.error('Listen Service Stop error! [ListenService.py:stop] --> %s' %e)
            return False

    def generator(self, tunnelgroup):
        '''监听等待并分支处理 accept'''

        globals.G_Log.debug('Listen generator Start.')

        while (self._isRun == True):
            try:
                sock, address = tunnelgroup._Listen_Socket.accept()

                tunnelworker = TunnelWorker()
                tunnelworker._TunnelGroup = tunnelgroup
                tunnelworker._Client_App_Socket = sock
                # put worker to WorkerQueue
                self._TunnelWorkerQueue.put(tunnelworker)

                # worker manager
                # add worker to _TunnelWorkerList
                ret = self._tunnelWorksManager('add', tunnelworker)
                # print this worker info
                globals.G_Log.info('accept: %s' %str(address))
            except Exception as e:
                globals.G_Log.error('listen generator error! [ListenService.py:generator] --> %s' %e)
