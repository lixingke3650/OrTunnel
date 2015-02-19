# !usr/bin/python
# -*- coding: utf-8 -*-
# Filename: HeartBeat.py

# std
import socket
import threading

# original
import Net

class HeartBeat():

	_Heart = 'I love you, give you my heart.'
	_PartnerSocket = None
	_isRun = False
	_HeartBeatCycle = 60
	_HeartBeatTimer = None
	_DeathCallBack = None
	count = 0

	def __init__(self, sock, time, deathfun):
		'''初始化
			sock: 连接目标socket
			time: 心跳周期
			deathfun: 失败后回调函数
		'''

		self._PartnerSocket = sock
		self._HeartBeatCycle = time
		self._DeathCallBack = deathfun

	def start(self):
		self._isRun = True
		self._HeartBeatTimer = threading.Timer(self._HeartBeatCycle, self.run)
		self._HeartBeatTimer.start()

	def stop(self):
		self._isRun = False
		self._HeartBeatTimer.cancel()

	def run(self):
		if (self._isRun == True):
			if (self.checkHeart() == False):
				self._DeathCallBack()
				self._isRun = False
				return

			self._HeartBeatTimer = threading.Timer(self._HeartBeatCycle, self.run)
			self._HeartBeatTimer.start()

	def checkHeart(self):
		return True

