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
from Client.TunnelWorker import *

__all__ = ['ListenService']

class ListenService():
    """ListenService服务
    监听本地连接，并读取数据存放到队列中"""

    # 数据队列
    _TunnelQueue = None
    # 隧道条数
    _TunnelGroupNumber = 0
    # 监听进程描述符
    _GeneratorThread = None
    # 隧道对象列表
    _TunnelGroupList = []
    # 隧道监听列表
    _Accepting_TunnelGroupList = []
    # 监听服务启动标识
    _isRun = None
    # 监听服务子通信进程维护列表

    def __init__(self, groupnumber, grouplist, tunnelqueue):
        '''监听服务初始化'''
        if (groupnumber > len(grouplist)):
            self._TunnelGroupNumber = len(grouplist)
        else:
            self._TunnelGroupNumber = groupnumber
        self._TunnelGroupList = grouplist
        self._TunnelQueue = tunnelqueue
        self._isRun = False

    def start(self):
        '''监听服务启动'''
        if (self._TunnelQueue == None):
            return False
        try:
            globals.G_Log.debug('Listen Service Start Start.')
            for i in range(self._TunnelGroupNumber):
                tunnelgroupinfo = self._TunnelGroupList[i]
                accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address = (tunnelgroupinfo[0], tunnelgroupinfo[1])
                accept_socket.bind(address)
                accept_socket.listen(globals.G_LISTEN_CONNECT_HOLDMAX)
                tunnelgroup = TunnelGroup()
                tunnelgroup._Accept_Socket = accept_socket
                tunnelgroup._Info = tunnelgroupinfo
                generatorThread = threading.Thread(target = self.generator, args = (tunnelgroup,))
                tunnelgroup._GeneratorThread = generatorThread
                self._Accepting_TunnelGroupList.append(tunnelgroup)
            self._isRun = True
            for j in range(len(self._Accepting_TunnelGroupList)):
                self._Accepting_TunnelGroupList[j]._GeneratorThread.start()
            globals.G_Log.debug('Listen Service Start End.')
            return True
        except Exception as e:
            globals.G_Log.error('Listen Service Start error! [ListenService.py:ListenService:start] --> %s' %e)

    def stop(self):
        '''监听服务停止'''
        if (self._isRun == False):
            return True
        try:
            globals.G_Log.debug('Listen Service Stop Start.')
            self._isRun = False
            for j in range(len(self._Accepting_TunnelGroupList)):
                self._Accepting_TunnelGroupList[j]._Accept_Socket.shutdown(socket.SHUT_RDWR)
                self._Accepting_TunnelGroupList[j]._Accept_Socket.close()
                self._Accepting_TunnelGroupList[j]._GeneratorThread.jion(10)
            globals.G_Log.debug('Listen Service Stop End.')
            return True
        except Exception as e:
            globals.G_Log.error('Listen Service Stop error! [ListenService.py:ListenService:stop] --> %s' %e)
            return False

    def generator(self, tunnelgroup):
        '''监听等待并分支处理 accept'''

        globals.G_Log.debug('Listen generator Start.')

        while (self._isRun == True):
            try:
                sock, address = tunnelgroup._Accept_Socket.accept()
                tunnelworker = TunnelWorker()
                tunnelworker._Info = tunnelgroup._Info
                tunnelworker._Client_App_Socket = sock
                # worker加入到队列
                self._TunnelQueue.put(tunnelworker)
            except Exception as e:
                globals.G_Log.error('listen generator error! [ListenService.py:ListenService:generator] --> %s' %e)
