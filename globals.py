#! usr/bin/python
# -*- coding: utf-8 -*-
# Filename: globals.py

__all__ = [ \
    'G_Log', 'G_LOG_NAME', 'G_LOG_LEVEL', 'G_SECRET_FLAG', \
    'G_SECRET_TYPE', 'G_TLS_CERT', 'G_TLS_KEY', 'G_TLS_CERT_VERIFY', \
    'G_SECRET_KEY', 'G_SOCKET_RECV_MAXSIZE', 'G_LISTEN_CONNECT_HOLDMAX', \
    'G_TUNNEL_NUM', 'G_TUNNEL_GROUP_LIST' \
]

# logger
G_Log = None
# log 文件名
G_LOG_NAME = 'OrTunnel'
# log 输出级别
G_LOG_LEVEL = 'INFO'
# 加解密开关switch
G_SECRET_FLAG = False
# 加解密方式
G_SECRET_TYPE = None
# SSL/TLS 证书
G_TLS_CERT = None
# SSL/TLS 私钥
G_TLS_KEY = None
# SSL/TLS 证书 (连接方证书，验证用)
G_TLS_CERT_VERIFY = None
# 密钥
G_SECRET_KEY = '1234567890ABCDEF'
# socket一次读取最大size
G_SOCKET_RECV_MAXSIZE = 65535
# 最大连接数
G_LISTEN_CONNECT_HOLDMAX = 0
# 隧道条数
G_TUNNEL_NUM = 0
# 隧道对象 列表结构： [(0:监听IP， 1:监听端口， 2:目标IP， 3:目标端口， 4:最大连接数), ...]
# G_TUNNEL_GROUP_LIST = [('0.0.0.0', 0, '0.0.0.0', 0, 5), ('0.0.0.0', 0, '0.0.0.0', 0, 10)]
G_TUNNEL_GROUP_LIST = []
