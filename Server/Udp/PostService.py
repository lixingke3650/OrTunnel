#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: PostService.py

# std
import socket
import threading

# original
from Tool import *
import Server.Udp.ListenService
import Server.Udp.PostService
import globals

__all__ = ['PostService']

class PostService():
    '''  '''
    _TunnelGroupList = None
    _TunnelWorkerQueue = None
    _WorkerThread = None
    _isRun = False

    def __init__(self, tunnelgrouplist, tunnelwokerqueue, tunnelworksmanager):
        '''  '''
        self._TunnelGroupList = tunnelgrouplist
        self._TunnelWorkerQueue = tunnelwokerqueue
        self._tunnelWorksManager = tunnelworksmanager
        self._isRun = False

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
                except:
                    # tunnel worker delete error
                    # 可能存在多重删除的情况，输出DEBUG日志
                    globals.G_Log.debug('Worker abolish delete error! [PostService.py:abolishworker] --> %s' %e)
        except EnvironmentError as e:
            # socket二次关闭，输出DEBUG日志
            globals.G_Log.debug('Worker abolish EnvironmentError! [PostService.py:abolishworker] --> %s' %e)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('Worker abolish AttributeError! [PostService.py:abolishworker] --> %s' %e)
        except Exception as e:
            globals.G_Log.error('Worker abolish error! [PostService.py:abolishworker] --> %s' %e)

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
        try:
            server_apps_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            appaddr = (tunnelworker._TunnelGroup._TargetIP, tunnelworker._TunnelGroup._TargetPort)
            server_apps_socket.connect(appaddr)
            tunnelworker._Server_App_Socket = server_apps_socket
            ctosthread = threading.Thread(target = self.ctosrun, args = (tunnelworker,))
            stocthread = threading.Thread(target = self.stocrun, args = (tunnelworker,))
            tunnelworker._CToSThread = ctosthread
            tunnelworker._SToCThread = stocthread
            ctosthread.start()
            stocthread.start()
        except Exception as e:
            globals.G_Log.error('Worker Launch error! [PostService.py:launchworker] --> %s' %e)

    def ctosrun(self, tunnelworker):
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
                if not buffer:
                    globals.G_Log.info('client socket close. [PostService.py:ctosrun]')
                    break
                tunnelworker._Server_App_Socket.sendall(debuffer(tunnelworker, buffer))

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post for client to server TypeError! [PostService.py:ctosrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post for client to server socket.error %d! [PostService.py:ctosrun] --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post for client to server socket.error %d! [PostService.py:ctosrun] --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post for client to server error! [PostService.py:ctosrun] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)

    def stocrun(self, tunnelworker):
        ''' '''
        globals.G_Log.info('ctosrun start.')

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
                    globals.G_Log.info('server socket close. [PostService.py:stocrun]')
                    break
                tunnelworker._Server_Client_Socket.sendto(enbuffer(tunnelworker, buffer), tunnelworker._FromClientAddr)

        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post for server to client TypeError! [PostService.py:stocrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post for server to client socket.error %d! [PostService.py:stocrun] --> %s' %(e.errno,e))
            else:
                globals.G_Log.error('data post for server to client socket.error %d! [PostService.py:stocrun] --> %s' %(e.errno,e))
        except Exception as e:
            globals.G_Log.error('data post for server to client error! [PostService.py:stocrun] --> %s' %e)
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
