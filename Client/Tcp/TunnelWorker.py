#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: TunnelWorker.py

# std


# original


__all__ = ['TunnelGroup', 'TunnelWorker']

class TunnelGroup():
    ''' '''
    _APPMethod = ''
    _ListenIP = ''
    _ListenPort = 0
    _TargetIP = ''
    _TargetPort = 0
    _Listen_Socket = None
    _GeneratorThread = None

class TunnelWorker():
    ''' '''
    _Client_App_Socket = None
    _Client_Server_Socket = None
    _CToSThread = None
    _StoCThread = None
    _isEnable = False
    _Crypt = None
    _TunnelGroup = None
