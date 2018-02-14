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
from Server.TunnelWorker import *

__all__ = ['ListenService']

class ListenService():
    '''ListenService service'''

    _TunnelWorkerQueue = None
    _TunnelGroupNumber = None
    _TunnelGroupInfo = None
    _TunnelGroupList = None
    _isRun = None
    _TunnelWorkThreadRLock = None
    _tunnelWorksManager = None

    def __init__(self, tunnelgrouplist, tunnelworkerqueue, tunnelworksmanager):
        ''''''
        if (globals.G_TUNNEL_NUM > len(globals.G_TUNNEL_GROUP_INFO)):
            self._TunnelGroupNumber = len(globals.G_TUNNEL_GROUP_INFO)
        else:
            self._TunnelGroupNumber = globals.G_TUNNEL_NUM
        self._TunnelGroupInfo = globals.G_TUNNEL_GROUP_INFO
        self._TunnelGroupList = tunnelgrouplist
        self._TunnelWorkerQueue = tunnelworkerqueue
        self._isRun = False
        self._tunnelWorksManager = tunnelworksmanager
        self._TunnelWorkThreadRLock = threading.RLock()

    def start(self):
        '''监听服务启动'''
        if (self._TunnelWorkerQueue == None):
            return False

        globals.G_Log.debug('Listen Service Start.')

        if (globals.G_TUNNEL_METHOD == 'TCP'):
            try:
                for i in range(self._TunnelGroupNumber):
                    tunnelgroupinfo = self._TunnelGroupInfo[i]
                    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, globals.G_SOCKET_UDP_SEND_BUFFERSIZE)
                    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.G_SOCKET_UDP_RECV_BUFFERSIZE)
                    globals.G_Log.info('listen socket send buffer size: %d' %(listen_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)))
                    globals.G_Log.info('listen socket recv buffer size: %d' %(listen_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)))

                    tunnelgroup = TunnelGroup()
                    tunnelgroup._Listen_Socket = listen_socket
                    tunnelgroup._ListenIP = tunnelgroupinfo[globals.GD_LISTENIP]
                    tunnelgroup._ListenPort = tunnelgroupinfo[globals.GD_LISTENPORT]
                    tunnelgroup._TargetIP = tunnelgroupinfo[globals.GD_TARGETIP]
                    tunnelgroup._TargetPort = tunnelgroupinfo[globals.GD_TARGETPORT]
                    tunnelgroup._Listen_Socket.bind((tunnelgroup._ListenIP, tunnelgroup._ListenPort))
                    tunnelgroup._Listen_Socket.listen(globals.G_LISTEN_CONNECT_HOLDMAX)
                    globals.G_Log.debug('Listen Service Start TCP listen: ')
                    globals.G_Log.debug(tunnelgroup._ListenIP)
                    globals.G_Log.debug(tunnelgroup._ListenPort)
                    generatorThread = threading.Thread(target = self.generator_tcp, args = (tunnelgroup,))
                    tunnelgroup._GeneratorThread = generatorThread
                    self._TunnelGroupList.append(tunnelgroup)
    
                self._isRun = True
                for j in range(len(self._TunnelGroupList)):
                    self._TunnelGroupList[j]._GeneratorThread.start()
                globals.G_Log.debug('Listen Service Start End.')
                return True
            except Exception as e:
                globals.G_Log.error('Listen Service Start error! [ListenService.py:ListenService:start] --> %s' %e)
        
        elif (globals.G_TUNNEL_METHOD == 'UDP'):
            try:
                for i in range(self._TunnelGroupNumber):
                    tunnelgroupinfo = self._TunnelGroupInfo[i]
                    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, globals.G_SOCKET_UDP_SEND_BUFFERSIZE)
                    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.G_SOCKET_UDP_RECV_BUFFERSIZE)
                    globals.G_Log.info('listen socket send buffer size: %d' %(listen_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)))
                    globals.G_Log.info('listen socket recv buffer size: %d' %(listen_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)))
    
                    tunnelgroup = TunnelGroup()
                    tunnelgroup._Listen_Socket = listen_socket
                    tunnelgroup._ListenIP = tunnelgroupinfo[globals.GD_LISTENIP]
                    tunnelgroup._ListenPort = tunnelgroupinfo[globals.GD_LISTENPORT]
                    tunnelgroup._TargetIP = tunnelgroupinfo[globals.GD_TARGETIP]
                    tunnelgroup._TargetPort = tunnelgroupinfo[globals.GD_TARGETPORT]
                    tunnelgroup._Listen_Socket.bind((tunnelgroup._ListenIP, tunnelgroup._ListenPort))
    
                    generatorThread = threading.Thread(target = self.generator_udp, args = (tunnelgroup,))
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

    def generator_tcp(self, tunnelgroup):
        '''监听等待并分支处理'''

        globals.G_Log.debug('Listen generator Start.')

        while (self._isRun == True):
            try:
                sock, address = tunnelgroup._Listen_Socket.accept()
                tunnelworker = TunnelWorker()
                tunnelworker._TunnelGroup = tunnelgroup
                tunnelworker._Server_Client_Socket = sock

                # protect data
                self.protectworker(tunnelworker)

                # put worker to WorkerQueue
                self._TunnelWorkerQueue.put(tunnelworker)

                # worker manager
                # add worker to _TunnelWorkerList
                ret = self._tunnelWorksManager('add', tunnelworker)
                # print this worker info
                # IO.printX('accept: %s' %str(address))
                globals.G_Log.info('accept: %s' %str(address))
            except Exception as e:
                globals.G_Log.error('listen generator error! [ListenService.py:ListenService:generator] --> %s' %e)

    def generator_udp(self, tunnelgroup):
        '''监听等待并分支处理'''

        globals.G_Log.debug('Listen generator Start.')

        sock = tunnelgroup._Listen_Socket

        try:
            while (self._isRun == True):
                buffer, server_client_addr = sock.recvfrom(globals.G_SOCKET_RECV_MAXSIZE_UDP)
                tunnelworker = self.get_tunnelworker(server_client_addr)
                if tunnelworker == None:
                    globals.G_Log.debug('Listen generator Create New TunnelWorker: %s.' %str(server_client_addr))
                    tunnelworker = TunnelWorker()
                    tunnelworker._TunnelGroup = tunnelgroup
                    tunnelworker._Server_Client_Socket = sock
                    tunnelworker._FromClientAddr = server_client_addr
                    tunnelworker._Buffer_Queue = queue.Queue(maxsize = globals.G_UDP_BUFFER_MAXQUEUE)
                    # tunnelworker._Buffer_Deque = deque()

                    # protect data
                    self.protectworker(tunnelworker)

                    # worker manager
                    # add worker to _TunnelWorkerList
                    self._TunnelWorkerQueue.put(tunnelworker)
                    ret = self._tunnelWorksManager('add', tunnelworker)
                tunnelworker._Buffer_Queue.put(buffer)
                # >>>>
                # globals.G_Log.info('tunnelworker._Buffer_Queue: %d ' %tunnelworker._Buffer_Queue.qsize())
                # <<<<
                # tunnelworker._Buffer_Deque.append(buffer)
        except Exception as e:
            globals.G_Log.error('listen generator error! [ListenService.py:generator] --> %s' %e)

    def get_tunnelworker(self, addr):
        for tunnelworker in self._tunnelWorksManager('get'):
            if tunnelworker._FromClientAddr == addr:
                return tunnelworker
        return None

    def protectworker(self, tunnelworker):
        # SSL Socket
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            tunnelworker._Server_Client_Socket = ssl.wrap_socket( tunnelworker._Server_Client_Socket ,  \
                                                                  server_side=True,               \
                                                                  certfile=globals.G_TLS_CERT,    \
                                                                  keyfile=globals.G_TLS_KEY,      \
                                                                  ssl_version=ssl.PROTOCOL_TLSv1)
        # ARC4 Crypt
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            tunnelworker._Crypt = Crypt.CrypterARC4(globals.G_SECRET_KEY)
        return
