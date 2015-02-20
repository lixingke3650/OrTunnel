#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: ListenService.py

# std
import socket
import threading
import Queue

# original
from Tool import *
import globals
import TunnelWorker

class ListenService():
	"""ListenService服务
	监听本地连接，并读取数据存放到队列中"""

	# 数据队列
	_TunnelQueue = None
	# 监听服务socket
	_ServiceSocket = None
	# 监听地址
	_ServerAddress = None
	# 监听连接最大数
	_ConnectMaximum = None
	# 监听进程描述符
	_GeneratorThread = None
	# 监听服务启动标识
	_isRun = None
	# 监听服务子通信进程维护列表

	def __init__(self, ip, port, tunnelqueue, maximum = 128):
		'''监听服务初始化'''

		self._TunnelQueue = tunnelqueue
		self._ServerAddress = (ip, port)
		self._ConnectMaximum = maximum
		self._isRun = False

	def start(self):
		'''监听服务启动'''

		globals.G_Log.info( 'Listen Service Start. [ListenService.py:ListenService:start]' )

		if (self._TunnelQueue == None):
			return False

		try:
			self._ServiceSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self._ServiceSocket.bind( self._ServerAddress )
			self._ServiceSocket.listen( self._ConnectMaximum )

			globals.G_Log.info( 'Listen %s:%s Start. [ListenService.py:ListenService:start]' % (self._ServerAddress[0], str(self._ServerAddress[1])) )

			self._GeneratorThread = threading.Thread( target = self.generator )
			self._isRun = True
			self._GeneratorThread.start()
			return True

		except Exception as e:
			globals.G_Log.error( 'Listen Service Start error! [ListenService.py:ListenService:start] --> %s' %e )

	def stop(self):
		'''监听服务停止'''

		if (self._isRun == False):
			return True

		try:
			self._ServiceSocket.shutdown( socket.SHUT_RDWR )
			self._ServiceSocket.close()
			self._ServiceSocket = None
			self._isRun = False
			self._GeneratorThread.jion(10)
			return True
		except Exception as e:
			globals.G_Log.error( 'Listen Service Stop error! [ListenService.py:ListenService:stop] --> %s' %e )
			return False

	def generator(self):
		'''监听等待并分支处理 accept'''

		globals.G_Log.info( 'generator Start. [ListenService.py:ListenService:generator]' )

		while (self._isRun == True):
			try:
				sock, address = self._ServiceSocket.accept()
				tunnelworker = TunnelWorker.TunnelWorker()
				tunnelworker._Client_Server_Socket = sock
				# worker加入到队列
				self._TunnelQueue.put(tunnelworker)

			except Exception as e:
				globals.G_Log.error( 'listen generator error! [ListenService.py:ListenService:generator] --> %s' %e )
