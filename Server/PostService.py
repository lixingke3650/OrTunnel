#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: PostService.py

# std
import socket
import threading
import time

# original
from Tool import *
import Server.ListenService
import Server.PostService
import globals

__all__ = ['PostService']

class PostService():
    '''  '''
    _TunnelGroupList = None
    _TunnelWorkerQueue = None
    _tunnelWorksManager = None
    _WorkerThread = None
    _isRun = False

    def __init__(self, tunnelgrouplist, tunnelwokerqueue, tunnelworksmanager):
        '''  '''
        self._TunnelGroupList = tunnelgrouplist
        self._TunnelWorkerQueue = tunnelwokerqueue
        self._tunnelWorksManager = tunnelworksmanager
        self._isRun = False
        # self._TunnelWorkThreadRLock = threading.RLock()

    def start(self):
        '''  '''
        if (self._TunnelWorkerQueue == None):
            return False
        try:
            self._WorkerThread = threading.Thread(target = self.workerlisten)
            self._isRun = True
            self._WorkerThread.start()
            return True
        except Exception as e:
            globals.G_Log.error('Worker Service Start error! --> %s' %e)
            return False

    def stop(self):
        '''  '''
        if (self._isRun == False):
            return True

        workerlist = self._tunnelWorksManager('get')
        if (workerlist == None):
            return True

        try:
            self._isRun = False
            # stop worker in the workerlist
            while tunnelworker in workerlist:
                self.abolishworker(tunnelworker)
            self._WorkerThread.join(10)
            return True
        except Exception as e:
            globals.G_Log.error('Worker Service Stop error! --> %s' %e)
            return False

    def abolishworker(self, tunnelworker):
        '''worker stop'''

        try:
            if (tunnelworker._isEnable == True):
                if (tunnelworker._Server_Client_Socket != None):
                    tunnelworker._Server_Client_Socket.shutdown(socket.SHUT_RDWR)
                    tunnelworker._Server_Client_Socket.close()
                    tunnelworker._Server_Client_Socket = None
                if (tunnelworker._Server_App_Socket != None):
                    tunnelworker._Server_App_Socket.shutdown(socket.SHUT_RDWR)
                    tunnelworker._Server_App_Socket.close()
                    tunnelworker._Server_App_Socket = None
                try:
                    ret = self._tunnelWorksManager('del', tunnelworker)
                    tunnelworker._isEnable = False
                except Exception as e:
                    # tunnel worker delete error
                    # 可能存在多重删除的情况，输出DEBUG日志
                    globals.G_Log.debug('Worker abolish delete error! --> %s' %e)
        except EnvironmentError as e:
            # socket二次关闭，输出DEBUG日志
            globals.G_Log.debug('Worker abolish EnvironmentError! --> %s' %e)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('Worker abolish AttributeError! --> %s' %e)
        except Exception as e:
            globals.G_Log.error('Worker abolish error! --> %s' %e)

    def workerlisten(self):
        ''' '''
        try:
            while True:
                tunnelworker = self._TunnelWorkerQueue.get()
                launchthread = threading.Thread(target = self.launchworker, args = (tunnelworker,))
                launchthread.start()
        except Exception as e:
            globals.G_Log.error('Worker abolish error! --> %s' %e)

    def launchworker(self, tunnelworker):
        ''' '''
        try:
            server_apps_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_apps_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, globals.G_SOCKET_RECV_MAXSIZE_UDP_APP)
            server_apps_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.G_SOCKET_RECV_MAXSIZE_UDP_APP)
            globals.G_Log.info('app socket send buffer size: %d' %(server_apps_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)))
            globals.G_Log.info('app socket recv buffer size: %d' %(server_apps_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)))
            appaddress = (tunnelworker._TunnelGroup._TargetIP, tunnelworker._TunnelGroup._TargetPort)
            globals.G_Log.info('connect: %s' %str(appaddress))
            server_apps_socket.connect(appaddress)
            tunnelworker._Server_App_Socket = server_apps_socket
            if (globals.G_TUNNEL_METHOD == 'TCP'):
                ctosthread = threading.Thread(target = self.ctosrun_tcp, args = (tunnelworker,))
                stocthread = threading.Thread(target = self.stocrun_tcp, args = (tunnelworker,))
            elif (globals.G_TUNNEL_METHOD == 'UDP'):
                ctosthread = threading.Thread(target = self.ctosrun_udp, args = (tunnelworker,))
                stocthread = threading.Thread(target = self.stocrun_udp, args = (tunnelworker,))
            tunnelworker._CToSThread = ctosthread
            tunnelworker._SToCThread = stocthread
            ctosthread.start()
            stocthread.start()
            tunnelworker._isEnable = True
        except Exception as e:
            globals.G_Log.error('Worker Launch error! --> %s' %e)

    def ctosrun_tcp(self, tunnelworker):
        ''''''
        debuffer = None
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            debuffer = self.arc4_debuffer
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            debuffer = self.ssl_debuffer
        else :
            debuffer = self.no_debuffer

        try:
            while True:
                buffer = tunnelworker._Server_Client_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info('client socket close.')
                    break
                tunnelworker._Server_App_Socket.sendall(debuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from client to server TypeError! --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from client to server socket.error %d! --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post from client to server socket.error %d! --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post from client to server error! --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def stocrun_tcp(self, tunnelworker):
        ''''''
        enbuffer = None
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            enbuffer = self.arc4_enbuffer
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            enbuffer = self.ssl_enbuffer
        else :
            enbuffer = self.no_enbuffer

        try:
            while True:
                buffer = tunnelworker._Server_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info('server socket close.')
                    break
                tunnelworker._Server_Client_Socket.sendall(enbuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from server to client TypeError! --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from server to client socket.error %d! --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post from server to client socket.error %d! --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post from server to client error! --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def ctosrun_udp(self, tunnelworker):
        ''' '''
        globals.G_Log.info('ctosrun start.')

        debuffer = None
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            debuffer = self.arc4_debuffer
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            debuffer = self.ssl_debuffer
        else :
            debuffer = self.no_debuffer

        try:
            while True:
                buffer = tunnelworker._Buffer_Queue.get()
                # >>>>
                # globals.G_Log.info('ctosrun data: %s' %buffer)
                # <<<<
                # buffer = tunnelworker._Buffer_Deque.leftpop()
                if not buffer:
                    globals.G_Log.info('client socket close.')
                    break
                tunnelworker._Server_App_Socket.sendall(debuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from client to server TypeError! --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from client to server socket.error %d! --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post from client to server socket.error %d! --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post from client to server error! --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def stocrun_udp(self, tunnelworker):
        ''' '''
        globals.G_Log.info('stocrun start.')

        enbuffer = None
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            enbuffer = self.arc4_enbuffer
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            enbuffer = self.ssl_enbuffer
        else :
            enbuffer = self.no_enbuffer

        try:
            while True:
                buffer = tunnelworker._Server_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE_UDP_APP)
                # >>>>
                # globals.G_Log.info('stocrun data size: %d' %len(buffer))
                # <<<<
                if not buffer:
                    globals.G_Log.info('server socket close.')
                    break
                tunnelworker._Server_Client_Socket.sendto(enbuffer(tunnelworker, buffer), tunnelworker._FromClientAddr)
                if (globals.G_SOCKET_SENTTO_DELAY_UDP > 0):
                    time.sleep(globals.G_SOCKET_SENTTO_DELAY_UDP)

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from server to client TypeError! --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from server to client socket.error %d! --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post from server to client socket.error %d! --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post from server to client error! --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def no_enbuffer(self, tunnelworker, buffer):
        return buffer

    def no_debuffer(self, tunnelworker, buffer):
        return buffer

    def ssl_enbuffer(self, tunnelworker, buffer):
        return buffer

    def ssl_debuffer(self, tunnelworker, buffer):
        return buffer

    def arc4_enbuffer(self, tunnelworker, buffer):
        return tunnelworker._Crypt.enCrypt(buffer)

    def arc4_debuffer(self, tunnelworker, buffer):
        return tunnelworker._Crypt.deCrypt(buffer)
