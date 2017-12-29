#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: ListenService.py

# std
import socket
import threading
import queue
import ssl

# original
from Tool import *
import globals
from Server.Udp.TunnelWorker import *

__all__ = ['ListenService']

class ListenService():
    '''ListenService service'''

    _TunnelWorkerQueue = None
    _TunnelWorkerList = None
    _ServiceSocket = None
    _ServerAddress = None
    _TunnelGroupNumber = None
    _TunnelGroupInfo = None
    _TunnelGroupList = None
    _isRun = None
    _TunnelWorkThreadRLock = None

    def __init__(self, tunnelgrouplist, tunnelworkerqueue):
        '''监听服务初始化'''
        if (globals.G_TUNNEL_NUM > len(globals.G_TUNNEL_GROUP_INFO)):
            self._TunnelGroupNumber = len(globals.G_TUNNEL_GROUP_INFO)
        else:
            self._TunnelGroupNumber = globals.G_TUNNEL_NUM
        self._TunnelGroupInfo = globals.G_TUNNEL_GROUP_INFO
        self._TunnelGroupList = tunnelgrouplist 
        self._TunnelWorkerQueue = tunnelworkerqueue
        self._isRun = False
        self._TunnelWorkerList = []
        self._TunnelWorkThreadRLock = threading.RLock()

    def start(self):
        '''监听服务启动'''
        if (self._TunnelWorkerQueue == None):
            return False

        try:
            globals.G_Log.debug('Listen Service Start. _TunnelGroupNumber %d' %self._TunnelGroupNumber)
            for i in range(self._TunnelGroupNumber):
                tunnelgroupinfo = self._TunnelGroupInfo[i]
                listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                tunnelgroup = TunnelGroup()
                tunnelgroup._Listen_Socket = listen_socket
                tunnelgroup._ListenIP = tunnelgroupinfo[0]
                tunnelgroup._ListenPort = tunnelgroupinfo[1]
                tunnelgroup._TargetIP = tunnelgroupinfo[2]
                tunnelgroup._TargetPort = tunnelgroupinfo[3]
                tunnelgroup._Listen_Socket.bind((tunnelgroup._ListenIP, tunnelgroup._ListenPort))
                globals.G_Log.debug('Listen Service Start UDP bind: ')
                globals.G_Log.debug(tunnelgroup._ListenIP)
                globals.G_Log.debug(tunnelgroup._ListenPort)

                generatorThread = threading.Thread(target = self.generator, args = (tunnelgroup,))
                tunnelgroup._GeneratorThread = generatorThread
                self._TunnelGroupList.append(tunnelgroup)

            self._isRun = True
            for j in range(len(self._TunnelGroupList)):
                self._TunnelGroupList[j]._GeneratorThread.start()
            globals.G_Log.debug('Listen Service Start End.')
            return True
        except Exception as e:
            globals.G_Log.error('Listen Service Start error! [ListenService.py:ListenService:start] --> %s' %e)

    def stop(self):
        '''监听服务停止'''

        # if (self._isRun == False):
        #     return True
        # try:
        #     globals.G_Log.debug('Listen Service Stop Start.')
        #     self._isRun = False
        #     for j in range(len(self._Accepting_TunnelGroupList)):
        #         self._Accepting_TunnelGroupList[j]._Listen_Socket.shutdown(socket.SHUT_RDWR)
        #         self._Accepting_TunnelGroupList[j]._Listen_Socket.close()
        #         self._Accepting_TunnelGroupList[j]._GeneratorThread.jion(10)
        #     globals.G_Log.debug('Listen Service Stop End.')
        #     return True
        # except Exception as e:
        #     globals.G_Log.error('Listen Service Stop error! [ListenService.py:ListenService:stop] --> %s' %e)
        #     return False

        if (self._isRun == False):
            return
        for tunnelworker in self._TunnelWorkerList:
            self.stop_worker(tunnelworker)
        return

    def stop_worker(self, tunnelworker):
        ''''''
        tunnelworker._Server_Client_Socket.shutdown(socket.SHUT_RDWR)
        tunnelworker._Server_Client_Socket.close()
        self.tunnelworksmanager('del', tunnelworker)

    def generator(self, tunnelgroup):
        '''监听等待并分支处理'''

        globals.G_Log.debug('Listen generator Start.')

        sock = tunnelgroup._Listen_Socket

        # # SSL Socket
        # if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
        #     sock = ssl.wrap_socket( sock,                           \
        #                             server_side=True,               \
        #                             certfile=globals.G_TLS_CERT,    \
        #                             keyfile=globals.G_TLS_KEY,      \
        #                             ssl_version=ssl.PROTOCOL_TLSv1)
        # # ARC4 Crypt
        # elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
        #     tunnelworker._Crypt = Crypt.CrypterARC4(globals.G_SECRET_KEY)

        try:
            while (self._isRun == True):
                buffer, server_client_addr = sock.recvfrom(globals.G_SOCKET_RECV_MAXSIZE)
                tunnelworker = self.get_tunnelworker(server_client_addr)
                if tunnelworker == None:
                    tunnelworker = TunnelWorker()
                    tunnelworker._TunnelGroup = tunnelgroup
                    tunnelworker._Server_Client_Socket = sock
                    tunnelworker._FromClientAddr = server_client_addr
                    tunnelworker._Buffer_Queue = queue.Queue(maxsize = globals.G_UDP_BUFFER_MAXQUEUE)
                    # SSL Socket
                    if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
                        sock = ssl.wrap_socket( sock,                           \
                                                server_side=True,               \
                                                certfile=globals.G_TLS_CERT,    \
                                                keyfile=globals.G_TLS_KEY,      \
                                                ssl_version=ssl.PROTOCOL_TLSv1)
                    # ARC4 Crypt
                    elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                        tunnelworker._Crypt = Crypt.CrypterARC4(globals.G_SECRET_KEY)
                    self._TunnelWorkerQueue.put(tunnelworker)
                    # self._TunnelWorkerList.append(tunnelworker)
                    ret = self.tunnelworksmanager('add', tunnelworker)
                    if (globals.G_LOG_LEVEL == 'DEBUG'):
                        IO.printX('worker add %d' %ret)
                tunnelworker._Buffer_Queue.put(buffer)
        except Exception as e:
            globals.G_Log.error('listen generator error! [ListenService.py:ListenService:generator] --> %s' %e)

    def get_tunnelworker(self, addr):
        for tunnelworker in self._TunnelWorkerList:
            if tunnelworker._FromClientAddr == addr:
                return tunnelworker
        return None

    def tunnelworksmanager(self, oper, tunnelworker):
        '''proxyworks add and del.
        oper: add or del'''

        # return work count
        ret = 0
        # thread lock
        self._TunnelWorkThreadRLock.acquire()
        try:
            if( oper == 'add' ):
                if ((tunnelworker in self._TunnelWorkerList) == False):
                    self._TunnelWorkerList.append(tunnelworker)
            elif( oper == 'del' ):
                if ((tunnelworker in self._TunnelWorkerList) == True):
                    self._TunnelWorkerList.remove(tunnelworker)
            ret = len(self._TunnelWorkerList)
        except Exception as e:
            globals.G_Log.error( 'tunnelworks add or del error! [PostService.py:PostService:tunnelworksmanager] --> %s' %e )
        # thread unlock
        self._TunnelWorkThreadRLock.release()
        # return work count
        return ret;