#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: TunnelWorker.py

# std


# original


__all__ = ['TunnelGroup', 'TunnelWorker']

class TunnelGroup():
    ''' '''
    _ListenIP = ''
    _ListenPort = 0
    _TargetIP = ''
    _TargetPort = 0
    _Listen_Socket = None
    _GeneratorThread = None

class TunnelWorker():
    ''' '''
    _Server_Client_Socket = None
    _Server_App_Socket = None
    _CToSThread = None
    _StoCThread = None
    _isEnable = False
    _Crypt = None
    _FromClientAddr = None
    _Buffer_Queue = None
    _Buffer_Deque = None
    _TunnelGroup = None
