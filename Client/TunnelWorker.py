#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: TunnelWorker.py

# std
# import queue

# original


__all__ = ['TunnelGroup', 'TunnelWorker']

class TunnelGroup():
    _Accept_Socket = None
    _Info = None
    _GeneratorThread = None

class TunnelWorker():
    '''隧道构造体，
    持有
      隧道socket(本地，远程两个)
      读取本地请求 - 发送至远端服务器 线程描述符
      读取远端服务器 - 回复至本地 线程描述符
    '''

    _Client_App_Socket = None
    _Client_Server_Socket = None
    _CToSThread = None
    _StoThread = None
    _isEnable = False
    _Crypt = None
    _Info = None