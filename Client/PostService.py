#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: PostService.py

# std
import socket
import threading
import struct
import ssl
import time

# original
from Tool import *
import Client.PostService
import globals

__all__ = ['PostService']

class PostService():
    '''  '''
    _TunnelGroupList = None
    _TunnelWorkerQueue = None
    _tunnelWorksManager = None
    _WorkerThread = None
    _isRun = False

    def __init__(self, tunnelgrouplist, tunnelworkerqueue, tunnelworksmanager):
        '''  '''
        self._TunnelGroupList = tunnelgrouplist
        self._TunnelWorkerQueue = tunnelworkerqueue
        self._tunnelWorksManager = tunnelworksmanager
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
            globals.G_Log.error('Worker Service Start error! [PostService.py:start] --> %s' %e)
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
            globals.G_Log.error('Worker Service Stop error! [PostService.py:stop] --> %s' %e)
            return False

    def abolishworker(self, tunnelworker):
        '''worker stop'''

        # try:
        if (tunnelworker._isEnable == True):
            if (tunnelworker._Client_App_Socket != None):
                try:
                    tunnelworker._Client_App_Socket.shutdown(socket.SHUT_RDWR)
                    tunnelworker._Client_App_Socket.close()
                except Exception as e:
                    globals.G_Log.debug('Worker abolish _Client_App_Socket error! [PostService.py:abolishworker] --> %s' %e)
                finally:
                    tunnelworker._Client_App_Socket = None
            if (tunnelworker._Client_Server_Socket != None):
                try:
                    tunnelworker._Client_Server_Socket.shutdown(socket.SHUT_RDWR)
                    tunnelworker._Client_Server_Socket.close()
                except Exception as e:
                    globals.G_Log.debug('Worker abolish _Client_Server_Socket error! [PostService.py:abolishworker] --> %s' %e)
                finally:
                    tunnelworker._Client_Server_Socket = None
            try:
                ret = self._tunnelWorksManager('del', tunnelworker)
                tunnelworker._isEnable = False
            except Exception as e:
                # tunnel worker delete error
                # 可能存在多重删除的情况，输出DEBUG日志
                globals.G_Log.debug('Worker abolish delete error! [PostService.py:abolishworker] --> %s' %e)
        # except EnvironmentError as e:
        #     # socket二次关闭，输出DEBUG日志
        #     globals.G_Log.debug('Worker abolish EnvironmentError! [PostService.py:abolishworker] --> %s' %e)
        # except AttributeError as e:
        #     # socket被关闭后无法读写，输出DEBUG日志
        #     globals.G_Log.debug('Worker abolish AttributeError! [PostService.py:abolishworker] --> %s' %e)
        # except Exception as e:
        #     globals.G_Log.error('Worker abolish error! [PostService.py:abolishworker] --> %s' %e)

    def workerlisten(self):
        ''' '''
        try:
            while True:
                tunnelworker = self._TunnelWorkerQueue.get()
                launchthread = threading.Thread(target = self.launchworker, args = (tunnelworker,))
                launchthread.start()
        except Exception as e:
            globals.G_Log.error('Worker abolish error! [PostService.py:workerlisten] --> %s' %e)

    def launchworker(self, tunnelworker):
        ''' '''
        globals.G_Log.info('launchworker start.')

        if (globals.G_TUNNEL_METHOD == 'TCP'):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, globals.G_SOCKET_UDP_SEND_BUFFERSIZE)
                # sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.G_SOCKET_UDP_RECV_BUFFERSIZE)
                # globals.G_Log.info('socket send buffer size: %d' %(sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)))
                # globals.G_Log.info('socket recv buffer size: %d' %(sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)))

                tunnelworker._Client_Server_Socket = sock
                serveraddress = (tunnelworker._TunnelGroup._TargetIP, tunnelworker._TunnelGroup._TargetPort)
                globals.G_Log.info('connect: %s' %str(serveraddress))

                # protect data
                self.protectworker(tunnelworker)
                tunnelworker._Client_Server_Socket.connect(serveraddress)
                ctosthread = threading.Thread(target = self.ctosrun_tcp, args = (tunnelworker,))
                stocthread = threading.Thread(target = self.stocrun_tcp, args = (tunnelworker,))
                tunnelworker._CToSThread = ctosthread
                tunnelworker._SToCThread = stocthread
                ctosthread.start()
                stocthread.start()
                tunnelworker._isEnable = True
            except Exception as e:
                globals.G_Log.error('Worker Launch error! [PostService.py:launchworker] --> %s' %e)
        
        elif (globals.G_TUNNEL_METHOD == 'UDP'):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, globals.G_SOCKET_UDP_SEND_BUFFERSIZE)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, globals.G_SOCKET_UDP_RECV_BUFFERSIZE)
                globals.G_Log.info('socket send buffer size: %d' %(sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)))
                globals.G_Log.info('socket recv buffer size: %d' %(sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)))
                tunnelworker._Client_Server_Socket = sock

                # protect data
                self.protectworker(tunnelworker)
                event = threading.Event()
                ctosthread = threading.Thread(target = self.ctosrun_udp, args = (tunnelworker, event))
                stocthread = threading.Thread(target = self.stocrun_udp, args = (tunnelworker, event))
                tunnelworker._CToSThread = ctosthread
                tunnelworker._SToCThread = stocthread
                ctosthread.start()
                stocthread.start()
            except Exception as e:
                globals.G_Log.error('Worker Launch error! [PostService.py:launchworker] --> %s' %e)


    def ctosrun_tcp(self, tunnelworker):
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
                buffer = tunnelworker._Client_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info('client socket close. [PostService.py:ctosrun_tcp]')
                    break
                tunnelworker._Client_Server_Socket.sendall(enbuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from server to client TypeError! [PostService.py:ctosrun_tcp] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from server to client socket.error! [PostService.py:ctosrun_tcp] --> %s' %e)
            else:
                globals.G_Log.error('data post from server to client socket.error! [PostService.py:ctosrun_tcp] --> %s' %e)
        except Exception as e:
            globals.G_Log.error('data post from server to client error! [PostService.py:ctosrun_tcp] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def stocrun_tcp(self, tunnelworker):
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
                buffer = tunnelworker._Client_Server_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info('server socket close. [PostService.py:stocrun_tcp]')
                    break
                tunnelworker._Client_App_Socket.sendall(debuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from server to client TypeError! [PostService.py:stocrun_tcp] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from server to client socket.error %d! [PostService.py:stocrun_tcp] --> %s' %(e.errno, e))
            else:
                globals.G_Log.error('data post from server to client socket.error %d! [PostService.py:stocrun_tcp] --> %s' %(e.errno, e))
        except Exception as e:
            globals.G_Log.error('data post from server to client error! [PostService.py:stocrun_tcp] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def ctosrun_udp(self, tunnelworker, event):
        ''' '''
        globals.G_Log.info('ctosrun start.')

        enbuffer = None
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            enbuffer = self.arc4_enbuffer
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            enbuffer = self.ssl_enbuffer
        else :
            enbuffer = self.no_enbuffer

        serveraddr = (tunnelworker._TunnelGroup._TargetIP, tunnelworker._TunnelGroup._TargetPort)

        try:
            while True:
                buffer = tunnelworker._Client_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE_UDP_APP)
                # >>>>
                # globals.G_Log.info('ctosrun data: %s' %buffer)
                # <<<<
                if not buffer:
                    globals.G_Log.info('client socket close. [PostService.py:ctosrun]')
                    break
                tunnelworker._Client_Server_Socket.sendto(enbuffer(tunnelworker, buffer), serveraddr)
                if (globals.G_SOCKET_SENTTO_DELAY_UDP > 0):
                    time.sleep(globals.G_SOCKET_SENTTO_DELAY_UDP)

                if not event.is_set():
                    event.set()

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from client to server TypeError! [PostService.py:ctosrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from client to server socket.error %d! [PostService.py:ctosrun] --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post from client to server socket.error %d! [PostService.py:ctosrun] --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post from client to server error! [PostService.py:ctosrun] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def stocrun_udp(self, tunnelworker, event):
        ''' '''
        globals.G_Log.info('stocrun start.')

        event.wait()

        debuffer = None
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            debuffer = self.arc4_debuffer
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            debuffer = self.ssl_debuffer
        else :
            debuffer = self.no_debuffer

        try:
            while True:
                buffer, addr = tunnelworker._Client_Server_Socket.recvfrom(globals.G_SOCKET_RECV_MAXSIZE_UDP)
                if not buffer:
                    globals.G_Log.info('server socket close. [PostService.py:stocrun]')
                    break
                # >>>>
                # globals.G_Log.info('stocrun data: %s' %buffer)
                # <<<<
                tunnelworker._Client_App_Socket.sendall(debuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post from server to client TypeError! [PostService.py:stocrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post from server to client socket.error %d! [PostService.py:stocrun] --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post from server to client socket.error %d! [PostService.py:stocrun] --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post from server to client error! [PostService.py:stocrun] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def protectworker(self, tunnelworker):
        # SSL Socket
        if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
            tunnelworker._Client_Server_Socket = ssl.wrap_socket( tunnelworker._Client_Server_Socket,   \
                                                                  ca_certs=globals.G_TLS_CERT_VERIFY, \
                                                                  cert_reqs=ssl.CERT_REQUIRED)
        # ARC4 Crypt
        elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
            tunnelworker._Crypt = Crypt.CrypterARC4(globals.G_SECRET_KEY)
        return

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

    def testTunnelGroup(self, groupnumber, grouplist):
        '''network test'''
        IO.printX('tunnel method is UDP. test skip.')
