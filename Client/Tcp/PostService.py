#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: PostService.py

# std
import socket
import threading
import struct
import ssl

# original
from Tool import *
import Client.Tcp.PostService
import globals

__all__ = ['PostService']

class PostService():
    '''  '''
    _TunnelGroupList = None
    _TunnelWorkerQueue = None
    _WorkerThread = None
    _StartingWorkerList = None
    _isRun = False

    def __init__(self, tunnelgrouplist, tunnelwokerqueue):
        '''  '''
        self._TunnelGroupList = tunnelgrouplist
        self._TunnelWorkerQueue = tunnelwokerqueue
        self._StartingWorkerList = []
        self._isRun = False
        self._TunnelWorkThreadRLock = threading.RLock()

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
            globals.G_Log.error('Worker Service Start error! [TunnelWorker.py:TunnelWorkerService:start] --> %s' %e)
            return False

    def stop(self):
        '''  '''
        if (self._isRun == False):
            return True
        if (self._StartingWorkerList == None):
            return True
        try:
            self._isRun = False
            # stop worker in the _StartingWorkerList
            while tunnelworker in self._StartingWorkerList:
                self.abolishworker(tunnelworker)
            self._WorkerThread.join(10)
            return True
        except Exception as e:
            globals.G_Log.error('Worker Service Stop error! [TunnelWorker.py:TunnelWorkerService:stop] --> %s' %e)
            return False

    def abolishworker(self, tunnelworker):
        '''worker stop'''

        return

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
                    ret = self.tunnelworksmanager('del', tunnelworker)
                    tunnelworker._isEnable = False
                    # LOG LEVEL是DEBUG时，输出运行信息
                    if (globals.G_LOG_LEVEL == 'DEBUG'):
                        IO.printX('worker del %d' %ret)
                except:
                    # tunnel worker delete error
                    # 可能存在多重删除的情况，输出DEBUG日志
                    globals.G_Log.debug('Worker abolish delete error! [TunnelWorker.py:TunnelWorkerService:abolishworker] --> %s' %e)
        except EnvironmentError as e:
            # socket二次关闭，输出DEBUG日志
            globals.G_Log.debug('Worker abolish EnvironmentError! [TunnelWorker.py:TunnelWorkerService:abolishworker] --> %s' %e)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('Worker abolish AttributeError! [TunnelWorker.py:TunnelWorkerService:abolishworker] --> %s' %e)
        except Exception as e:
            globals.G_Log.error('Worker abolish error! [TunnelWorker.py:TunnelWorkerService:abolishworker] --> %s' %e)

    def workerlisten(self):
        ''' '''
        try:
            while True:
                tunnelworker = self._TunnelWorkerQueue.get()
                launchthread = threading.Thread(target = self.launchworker, args = (tunnelworker,))
                launchthread.start()
        except Exception as e:
            globals.G_Log.error('Worker abolish error! [TunnelWorker.py:TunnelWorkerService:workerlisten] --> %s' %e)

    def launchworker(self, tunnelworker):
        ''' '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # SSL Socket
            if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
                sock = ssl.wrap_socket( sock,                               \
                                        ca_certs=globals.G_TLS_CERT_VERIFY, \
                                        cert_reqs=ssl.CERT_REQUIRED)
            # ARC4 Crypt
            elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                tunnelworker._Crypt = Crypt.CrypterARC4(globals.G_SECRET_KEY)
            serveraddress = (tunnelworker._TunnelGroup._TargetIP, tunnelworker._TunnelGroup._TargetPort)
            sock.connect(serveraddress)
            tunnelworker._Client_Server_Socket = sock
            ctosthread = threading.Thread(target = self.ctosrun, args = (tunnelworker,))
            stocthread = threading.Thread(target = self.stocrun, args = (tunnelworker,))
            tunnelworker._CToSThread = ctosthread
            tunnelworker._SToCThread = stocthread
            ctosthread.start()
            stocthread.start()
        except Exception as e:
            globals.G_Log.error('Worker Launch error! [TunnelWorker.py:TunnelWorkerService:launchworker] --> %s' %e)

    def ctosrun(self, tunnelworker):
        ''''''

        try:
            # ARC4
            if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                while True:
                    buffer = tunnelworker._Client_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                    if not buffer:
                        globals.G_Log.info( 'client socket close. [PostService.py:PostService:ctosrun]')
                        break
                    tunnelworker._Client_Server_Socket.sendall(tunnelworker._Crypt.enCrypt(buffer))
            else:
                while True:
                    buffer = tunnelworker._Client_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                    if not buffer:
                        globals.G_Log.info( 'client socket close. [PostService.py:PostService:ctosrun]')
                        break
                    tunnelworker._Client_Server_Socket.sendall(buffer)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug( 'data post for server to client TypeError! [PostService.py:PostService:ctosrun] --> %s' %e )
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug( 'data post for server to client socket.error! [PostService.py:PostService:ctosrun] --> %s' %e )
            else:
                globals.G_Log.error( 'data post for server to client socket.error! [PostService.py:PostService:ctosrun] --> %s' %e )
        except Exception as e:
            globals.G_Log.error( 'data post for server to client error! [PostService.py:PostService:ctosrun] --> %s' %e )
        finally:
            self.abolishworker(tunnelworker)

    def stocrun(self, tunnelworker):
        ''''''
        try:
            if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                while True:
                    buffer = tunnelworker._Client_Server_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                    if not buffer:
                        globals.G_Log.info( 'server socket close. [PostService.py:PostService:stocrun]')
                        break
                    tunnelworker._Client_App_Socket.sendall(tunnelworker._Crypt.deCrypt(buffer))
            else:
                while True:
                    buffer = tunnelworker._Client_Server_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                    if not buffer:
                        globals.G_Log.info( 'server socket close. [PostService.py:PostService:stocrun]')
                        break
                    tunnelworker._Client_App_Socket.sendall(buffer)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post for server to client TypeError! [PostService.py:PostService:stocrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post for server to client socket.error %d! [PostService.py:PostService:stocrun] --> %s' %(e.errno, e))
            else:
                globals.G_Log.error('data post for server to client socket.error %d! [PostService.py:PostService:stocrun] --> %s' %(e.errno, e))
        except Exception as e:
            globals.G_Log.error('data post for server to client error! [PostService.py:PostService:stocrun] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def testTunnelGroup(self, groupnumber, grouplist):
        '''network test'''

        IO.printX('tunnel method is UDP. test skip.')
