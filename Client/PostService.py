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
import Client.ListenService
import Client.PostService
import globals

__all__ = ['PostService']

class PostService():
    """PostService
    数据发送服务(双向)"""

    # 数据队列
    _TunnelQueue = None
    # 发送进程描述符
    _PostThread = None
    # 发送目标地址
    _PostAddress = None
    # 运行标识
    _isRun = None
    # 送信服务列表
    _TunnelWorks = []
    # 送信服务列表维护用线程锁
    _TunnelWorkThreadRLock = None


    def __init__(self, ip, port, tunnelqueue):
        '''送信服务初始化'''

        self._TunnelQueue = tunnelqueue
        self._PostAddress = (ip, port)
        self._isRun = False
        self._TunnelWorkThreadRLock = threading.RLock()


    def start(self):
        '''数据发送服务启动'''

        if (self._TunnelQueue == None):
            return False
        try:
            self._PostThread = threading.Thread( target = self.postrun )
            self._isRun = True
            self._PostThread.start()
            return True
        except Exception as e:
            globals.G_Log.error( 'Post Service Start error! [PostService.py:PostService:start] --> %s' %e )
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
            globals.G_Log.error( 'Listen Service Stop error! [ListenService.py:ListenService:stop] --> %s' %e )
            return False


    def postrun(self):
        '''数据发送(双向)'''

        try:
            while (self._isRun == True):
                tunnelworker = self._TunnelQueue.get()
                launchthread = threading.Thread( target = self.launchworker, args = (tunnelworker,) )
                launchthread.start()
        except Exception as e:
            globals.G_Log.error( 'Post Service run error! [PostService.py:PostService:postrun] --> %s' %e )


    def launchworker(self, tunnelworker):
        '''开启一条隧道进行通信
        '''

        try:
            servicesock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            # SSL Socket
            if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
                servicesock = ssl.wrap_socket(  servicesock,                        \
                                                ca_certs=globals.G_TLS_CERT_VERIFY, \
                                                cert_reqs=ssl.CERT_REQUIRED)
            # ARC4 Crypt
            elif (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                tunnelworker._Crypt = Crypt.CrypterARC4(globals.G_SECRET_KEY)
            servicesock.connect( self._PostAddress )
            tunnelworker._ServerSocket = servicesock
            ctosthread = threading.Thread( target = self.ctosrun, args = (tunnelworker,) )
            stocthread = threading.Thread( target = self.stocrun, args = (tunnelworker,) )
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
            globals.G_Log.error( 'Worker Launch error! [PostService.py:PostService:launchworker] --> %s' %e )


    def abolishworker(self, tunnelworker):
        '''worker 停止
        '''

        try:
            if (tunnelworker._isEnable == True):
                if (tunnelworker._ClientSocket != None):
                    tunnelworker._ClientSocket.shutdown( socket.SHUT_RDWR )
                    tunnelworker._ClientSocket.close()
                    tunnelworker._ClientSocket = None
                if (tunnelworker._ServerSocket != None):
                    tunnelworker._ServerSocket.shutdown( socket.SHUT_RDWR )
                    tunnelworker._ServerSocket.close()
                    tunnelworker._ServerSocket = None
                try:
                    ret = self.tunnelworksmanager('del', tunnelworker)
                    tunnelworker._isEnable = False
                    # LOG LEVEL是DEBUG时，输出运行信息
                    if (globals.G_LOG_LEVEL == 'DEBUG'):
                        IO.printX('worker del %d' %ret)
                except:
                    # tunnel worker delete error
                    # 可能存在多重删除的情况，输出DEBUG日志
                    globals.G_Log.debug( 'Worker abolish delete error! [PostService.py:PostService:abolishworker] --> %s' %e )
        except EnvironmentError as e:
            # socket二次关闭，输出DEBUG日志
            globals.G_Log.debug( 'Worker abolish EnvironmentError! [PostService.py:PostService:abolishworker] --> %s' %e )
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug( 'Worker abolish AttributeError! [PostService.py:PostService:abolishworker] --> %s' %e )
        except Exception as e:
            globals.G_Log.error( 'Worker abolish error! [PostService.py:PostService:abolishworker] --> %s' %e )


    def ctosrun(self, tunnelworker):
        '''循环读取本地数据发送到远程服务器
        '''

        try:
            while True:
                buffer = tunnelworker._ClientSocket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info( 'client socket close. [PostService.py:PostService:ctosrun]')
                    break
                if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                    buffer = tunnelworker._Crypt.enCrypt(buffer)
                tunnelworker._ServerSocket.sendall( buffer )
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
        '''循环读取远程服务器数据发送到本地
        '''

        try:
            while True:
                buffer = tunnelworker._ServerSocket.recv(globals.G_SOCKET_RECV_MAXSIZE)
                if not buffer:
                    globals.G_Log.info( 'server socket close. [PostService.py:PostService:stocrun]')
                    break
                if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'ARC4'):
                    buffer = tunnelworker._Crypt.deCrypt(buffer)
                tunnelworker._ClientSocket.sendall(buffer)
        except AttributeError as e:
            # socket被关闭后无法读写，输出DEBUG日志
            globals.G_Log.debug( 'data post for server to client TypeError! [PostService.py:PostService:stocrun] --> %s' %e )
        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053 or e.errno == 10058:
                # socket主动关闭的情况下，输出DEBUG日志
                globals.G_Log.debug( 'data post for server to client socket.error! [PostService.py:PostService:stocrun] --> %s' %e )
            else:
                globals.G_Log.error( 'data post for server to client socket.error! [PostService.py:PostService:stocrun] --> %s' %e )
        except Exception as e:
            globals.G_Log.error( 'data post for server to client error! [PostService.py:PostService:stocrun] --> %s' %e )
        finally:
            self.abolishworker(tunnelworker)


    def tunnelworksmanager( self, oper, tunnelworker ):
        '''proxyworks add and del.
        oper: add or del'''

        # 返回值，当前work总数
        ret = 0
        # thread lock
        self._TunnelWorkThreadRLock.acquire()
        try:
            if( oper == 'add' ):
                if ((tunnelworker in self._TunnelWorks) == False):
                    self._TunnelWorks.append( tunnelworker )
            elif( oper == 'del' ):
                if ((tunnelworker in self._TunnelWorks) == True):
                    self._TunnelWorks.remove( tunnelworker )
            ret = len( self._TunnelWorks )
        except Exception as e:
            globals.G_Log.error( 'tunnelworks add or del error! [PostService.py:PostService:tunnelworksmanager] --> %s' %e )
        # thread unlock
        self._TunnelWorkThreadRLock.release()
        # 返回当前work总数
        return ret;


    def testing(self):
        '''送信服务测试
        测试服务端能否连通
        '''

        try:
            # 利用socket connect来判断服务端能否连接
            testsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            # SSL Socket
            if (globals.G_SECRET_FLAG == True and globals.G_SECRET_TYPE == 'SSL'):
                testsock = ssl.wrap_socket( testsock,                       \
                                                ca_certs=globals.G_TLS_CERT_VERIFY, \
                                                cert_reqs=ssl.CERT_REQUIRED)
            testsock.connect( self._PostAddress )
            # socket关闭
            testsock.shutdown( socket.SHUT_RDWR )
            testsock.close()
            return True

        except Exception as e:
            return False
