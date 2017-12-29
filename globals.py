#! usr/bin/python
# -*- coding: utf-8 -*-
# Filename: globals.py

__all__ = [ \
    'G_MODE', 'G_Log', 'G_LOG_NAME', 'G_LOG_LEVEL', 'G_SECRET_FLAG', \
    'G_SECRET_TYPE', 'G_TLS_CERT', 'G_TLS_KEY', 'G_TLS_CERT_VERIFY', \
    'G_SECRET_KEY', 'G_SOCKET_RECV_MAXSIZE', 'G_LISTEN_CONNECT_HOLDMAX', \
    'G_TUNNEL_METHOD', 'G_TUNNEL_NUM', 'G_TUNNEL_GROUP_INFO', \
    'G_UDP_BUFFER_MAXQUEUE' \
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
# hold socket max 
G_LISTEN_CONNECT_HOLDMAX = 0
# tunnel method
G_TUNNEL_METHOD = None
# tunnel num
G_TUNNEL_NUM = 0
# tunnel info ： [('0.0.0.0', 0, '0.0.0.0', 0, 5), ('0.0.0.0', 0, '0.0.0.0', 0, 10)]
G_TUNNEL_GROUP_INFO = []
# udp buffer queue max num
G_UDP_BUFFER_MAXQUEUE = 1024