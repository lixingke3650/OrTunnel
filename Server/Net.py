# !usr/bin/python
# -*- coding: utf-8 -*-
# Filename: Net.py

# std
import socket


class NetSocket():
	'''socket封装
	提供分包，心跳功能。
	包协议 : 控制码(1byte)+包体大小(8byte)+包体
			控制码: 0-正常数据 以外-控制数据(1:心跳发送 2:心跳回应)
	'''

	# std socket
	_Socket = None

	# recv缓存区
	_RecvBuffer = (0, b'')

	# 心跳功能相关
	_isHeartBeat = False
	_MyHeart = 'I love you, give you my heart.'
	_HeartBeatCallBack = None



	def __init__(self, family = socket.AF_INET, type = socket.SOCK_STREAM, proto = 0, fileno = None):
		'''构造函数'''
		self._Socket = socket.socket(family, type, proto, fileno)

	def getSocket(self):
		'''获取系统socket，以方便执行未提供的功能'''
		return self._Socket

	def accept(self):
		return self._Socket.accept()

	def bind(self, address):
		return self._Socket.bind(address)

	def close(self):
		return self._Socket.close()

	def connect(self, address):
		return self._Socket.connect(address)

	def connect_ex(self, address):
		return self._Socket.connect_ex(address)

	def fileno(self):
		return self._Socket.fileno()

	def listen(self, backlog):
		return self._Socket.listen(backlog)

	def settimeout(self, value):
		return self._Socket.settimeout(value)

	def shutdown(self, how):
		return self._Socket.shutdown(how)

	def setsockopt(self, level, optname, value):
		return self._Socket.setsockopt(level, optname, value)

	def setHeartBeatCallBack(self, callfunc):
		self._HeartBeatCallBack = callfunc

	def enableHeartBeat(self):
		self._isHeartBeat = True

	def disableHeartBeat(self):
		self._isHeartBeat = False

	def send(self, buffer, control = 0):
		'''send重写，追加分包和控制功能
		最大发送数据为67108864(64GB),超出则返回-999
		'''

		size = len(buffer)
		if (size > 67108864):
			return (-999)

		self._Socket.send(str(control))
		self._Socket.send(str(size).zfill(8))
		return self._Socket.send(buffer)

	def recv(self, bufsize):
		'''recv重写，追加分包和控制功能
		- 若缓存区中有数据则先返回缓存中的数据
		- 若缓存区中数据大于bufsize，则返回bufsize大小的数据，其余留存在缓存区
		- 每次返回一个包的数据
		- 若包内数据大于bufsize，则返回bufsize大小的数据，其余存入缓存区

		'''

		buffer = b''

		# 若缓存区中有数据则先返回缓存中的数据
		if (self._RecvBuffer[0] > bufsize):
			self._RecvBuffer[0] = self._RecvBuffer[0] - bufsize
			buffer = self._RecvBuffer[1][0:bufsize]
			self._RecvBuffer[1] = self._RecvBuffer[:-self._RecvBuffer[0]]
			return buffer

		# 包解析
		control = self._Socket.recv(1)
		if not control:
			return control
		size = self._Socket.recv(8)
		if not size:
			return size
		size = len(size)
		sizetmp = 0
		while True:
			buffer += self._Socket.recv(size)
			sizetmp = len(buffer)
			if ( sizetmp >= size):
				break

		# 0 - 正常数据
		if (control == '0'):
			if (sizetmp <= bufsize):
				return buffer
			else:
				self._RecvBuffer[0] = sizetmp - bufsize
				self._RecvBuffer[1] = buffer[:-self._RecvBuffer[0]]
				return buffer[0:bufsize]
		# 0以外 - 控制数据,处理待追加
		else:
			pass
