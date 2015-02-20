#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: TunnelWorker.py

# std
import Queue

# original


class TunnelWorker():
	'''隧道构造体，
	持有
	  隧道socket(客户端，应用两个)
	  读取本地请求 - 发送至远端服务器 线程描述符
	  读取远端服务器 - 回复至本地 线程描述符
	'''

	_Client_Server_Socket = None
	_Server_App_Socket = None
	_CToSThread = None
	_StoCThread = None
	_isEnable = False
