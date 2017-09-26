#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: PostService.py

# std
import socket
import threading

# original
from Tool import *
import Server.ListenService
import Server.PostService
import globals

__all__ = ['PostService']

class PostService():
    """PostService
    数据发送服务(双向)"""

    # 数据队列
    _TunnelQueue = None
    # 发送进程描述符
    _PostThread = None
    # 运行标识
    _isRun = None
    # 送信服务列表
    _TunnelWorks = []
    # 送信服务列表维护用线程锁
    _TunnelWorkThreadRLock = None


    def __init__(self, tunnelqueue):
        '''送信服务初始化'''
        self._TunnelQueue = tunnelqueue
        self._isRun = False
        self._TunnelWorkThreadRLock = threading.RLock()


    def start(self):
        '''数据发送服务启动'''

        if (self._TunnelQueue == None):
            return False
        try:
            self._PostThread = threading.Thread(target = self.postrun)
            self._isRun = True
            self._PostThread.start()
            return True
        except Exception as e:
            globals.G_Log.error('Post Service Start error! [PostService.py:PostService:start] --> %s' %e)
            return False


    def stop(self):
        '''送信服务停止'''

        if (self._isRun == False):
            return True
        try:
            self._isRun = False
            # 列表中worker停止
            while tunnelworker in self._TunnelWorks:
                self.abolishworker(tunnelworker)
            self._PostThread.join(10)
            return True
        except Exception as e:
            globals.G_Log.error('Listen Service Stop error! [ListenService.py:ListenService:stop] --> %s' %e)
            return False


    def postrun(self):
        '''数据发送(双向)'''

        try:
            while (self._isRun == True):
                tunnelworker = self._TunnelQueue.get()
                launchthread = threading.Thread(target = self.launchworker, args = (tunnelworker,))
                launchthread.start()
                
        except Exception as e:
            globals.G_Log.error('Post Service run error! [PostService.py:PostService:postrun] --> %s' %e)


    def launchworker(self, tunnelworker):
        '''开启一条隧道的通信工作
        '''

        try:
            servicesock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            servicesock.connect((tunnelworker._Info[2], tunnelworker._Info[3]))
            tunnelworker._Server_App_Socket = servicesock
            ctosthread = threading.Thread(target = self.ctosrun, args = (tunnelworker,))
            stocthread = threading.Thread(target = self.stocrun, args = (tunnelworker,))
            tunnelworker._CToSThread = ctosthread
            tunnelworker._SToCThread = stocthread
            ctosthread.start()
            stocthread.start()
            tunnelworker._isEnable = True
            ret = self.tunnelworksmanager('add', tunnelworker)
            # LOG LEVEL是DEBUG时，输出运行信息
            if (globals.G_LOG_LEVEL == 'DEBUG'):
                IO.printX('worker add %d' %ret)
        except Exception as e:
            globals.G_Log.error('Worker Launch error! [PostService.py:PostService:launchworker] --> %s' %e)


    def abolishworker(self, tunnelworker):
        '''worker 停止
        '''

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
                    globals.G_Log.debug('Worker abolish delete error! [PostService.py:PostService:abolishworker] --> %s' %e)
        except EnvironmentError as e:
            # socket二次关闭，输出DEBUG日志
            globals.G_Log.debug('Worker abolish EnvironmentError! [PostService.py:PostService:abolishworker] --> %s' %e)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('Worker abolish AttributeError! [PostService.py:PostService:abolishworker] --> %s' %e)
        except Exception as e:
            globals.G_Log.error('Worker abolish error! [PostService.py:PostService:abolishworker] --> %s' %e)


    def ctosrun(self, tunnelworker):
        '''循环读取客户端数据发送给应用
        '''

        try:
            if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                while True:
                    buffer = tunnelworker._Server_Client_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                    if not buffer:
                        globals.G_Log.info('client socket close. [PostService.py:PostService:ctosrun]')
                        break
                    tunnelworker._Server_App_Socket.sendall(tunnelworker._Crypt.deCrypt(buffer))
            else:
                while True:
                    buffer = tunnelworker._Server_Client_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                    if not buffer:
                        globals.G_Log.info('client socket close. [PostService.py:PostService:ctosrun]')
                        break
                    tunnelworker._Server_App_Socket.sendall(buffer)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post for client to server TypeError! [PostService.py:PostService:ctosrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post for client to server socket.error! [PostService.py:PostService:ctosrun] --> %s' %e)
            else:
                globals.G_Log.error('data post for client to server socket.error! [PostService.py:PostService:ctosrun] --> %s' %e)
        except Exception as e:
            globals.G_Log.error('data post for client to server error! [PostService.py:PostService:ctosrun] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)


    def stocrun(self, tunnelworker):
        '''循环读取应用数据发送到远程客户端
        '''

        try:
            while True:
                buffer = tunnelworker._Server_App_Socket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info('server socket close. [PostService.py:PostService:stocrun]')
                    break
                if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                    buffer = tunnelworker._Crypt.enCrypt(buffer)
                tunnelworker._Server_Client_Socket.sendall( buffer )
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug('data post for server to client TypeError! [PostService.py:PostService:stocrun] --> %s' %e)
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug('data post for server to client socket.error! [PostService.py:PostService:stocrun] --> %s' %e)
            else:
                globals.G_Log.error('data post for server to client socket.error! [PostService.py:PostService:stocrun] --> %s' %e)
        except Exception as e:
            globals.G_Log.error('data post for server to client error! [PostService.py:PostService:stocrun] --> %s' %e)
        finally:
            self.abolishworker(tunnelworker)


    def tunnelworksmanager(self, oper, tunnelworker):
        '''proxyworks add and del.
        oper: add or del'''

        # 返回值，当前work总数
        ret = 0
        # thread lock
        self._TunnelWorkThreadRLock.acquire()
        try:
            if (oper == 'add'):
                if ((tunnelworker in self._TunnelWorks) == False):
                    self._TunnelWorks.append(tunnelworker)
            elif (oper == 'del'):
                if ((tunnelworker in self._TunnelWorks) == True):
                    self._TunnelWorks.remove(tunnelworker)
            ret = len(self._TunnelWorks)
        except Exception as e:
            globals.G_Log.error('tunnelworks add or del error! [PostService.py:PostService:tunnelworksmanager] --> %s' %e)
        # thread unlock
        self._TunnelWorkThreadRLock.release()
        # 返回当前work总数
        return ret;
