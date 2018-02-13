#! usr/bin/python
# -*- coding: utf-8 -*-
# Filename: globals.py

__all__ = [ \
    'G_MODE', 'G_Log', 'G_LOG_NAME', 'G_LOG_LEVEL', 'G_SECRET_FLAG', \
    'G_SECRET_TYPE', 'G_TLS_CERT', 'G_TLS_KEY', 'G_TLS_CERT_VERIFY', \
    'G_SECRET_KEY', 'G_SOCKET_RECV_MAXSIZE', 'G_SOCKET_RECV_MAXSIZE_UDP', \
    'G_SOCKET_RECV_MAXSIZE_UDP_APP', 'G_SOCKET_SENTTO_DELAY_UDP',         \
    'G_SOCKET_UDP_SEND_BUFFERSIZE', 'G_SOCKET_UDP_RECV_BUFFERSIZE'        \
    'G_LISTEN_CONNECT_HOLDMAX', 'G_TUNNEL_METHOD', 'G_TUNNEL_NUM',        \
    'G_TUNNEL_GROUP_INFO', 'G_UDP_BUFFER_MAXQUEUE', 'GD_APPMETHOD',       \
    'GD_LISTENIP', 'GD_LISTENPORT', 'GD_TARGETIP', 'GD_TARGETPORT'        \
]

# config file
G_CONFIG_FILE = 'ortunnel.conf'
# work mode
G_MODE = None
# logger
G_Log = None
# log name
G_LOG_NAME = 'ortunnel'
# log output level
G_LOG_LEVEL = 'INFO'
# secret switch
G_SECRET_FLAG = False
# secret type
G_SECRET_TYPE = None
# SSL/TLS cert
G_TLS_CERT = None
# SSL/TLS secret key
G_TLS_KEY = None
# SSL/TLS secret verify (Unused)
G_TLS_CERT_VERIFY = None
# ARC4 secret key
G_SECRET_KEY = '1234567890ABCDEF'
# socket recv maxsize
G_SOCKET_RECV_MAXSIZE = 65535
# socket recv maxsize
G_SOCKET_RECV_MAXSIZE_UDP = 8192*4
# socket recv maxsize
G_SOCKET_RECV_MAXSIZE_UDP_APP = G_SOCKET_RECV_MAXSIZE_UDP
# socket udp sentto time delay (s)
G_SOCKET_SENTTO_DELAY_UDP = 0.01
# socket udp sent buffer size
G_SOCKET_UDP_SEND_BUFFERSIZE = G_SOCKET_RECV_MAXSIZE_UDP
# socket udp recv buffer size
G_SOCKET_UDP_RECV_BUFFERSIZE = G_SOCKET_UDP_SEND_BUFFERSIZE
# hold socket max 
G_LISTEN_CONNECT_HOLDMAX = 0
# tunnel method
G_TUNNEL_METHOD = None
# tunnel num
G_TUNNEL_NUM = 0
# tunnel info ： [('TCP', 0.0.0.0', 0, '0.0.0.0', 0, 5), ('UDP', 0.0.0.0', 0, '0.0.0.0', 0, 10)]
G_TUNNEL_GROUP_INFO = []
# udp buffer queue max num
G_UDP_BUFFER_MAXQUEUE = 128

##
GD_APPMETHOD = 0
GD_LISTENIP = 1
GD_LISTENPORT = 2
GD_TARGETIP = 3
GD_TARGETPORT = 4