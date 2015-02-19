#! usr/bin/python
# -*- coding: utf-8 -*-
# Filename: globals.py

# original
# import Tool

# logger
G_Log = None
# log 文件名
G_LOG_NAME = 'OrTunnel'
# log 输出级别
G_LOGLEVEL = 'INFO'
# 加密解密开关switch
G_SECRET_FLAG = False
# 密钥
G_SECRET_KEY = '1234567890ABCDEF'

# socket一次读取最大size
G_SOCKET_RECV_MAXSIZE = 65535

# 远端服务器地址
G_SERVER_HOST = '0.0.0.0'
# 远端服务器端口
G_SERVER_PORT = 0
# 本地监视IP
G_CLIENT_IP = '0.0.0.0'
# 本地监视端口
G_CLIENT_PORT = 0
# 最大连接数
G_CLIENT_CONNECT_MAXNUMBER = 0

# 目标应用IP地址
G_TARGET_HOST = '0.0.0.0'
# 目标应用端口
G_TARGET_PORT = 0
# 监视IP
G_LISTEN_IP = '0.0.0.0'
# 监视端口
G_LISTEN_PORT = 0
# 最大连接数
G_LISTEN_CONNECT_MAXNUMBER = 0
