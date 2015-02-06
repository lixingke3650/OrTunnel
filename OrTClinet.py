#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: OrTClient.py

# std
import sys
import socket

# orignal
import globals
import Tool

# 版本说明
# 0.10：基本功能实现
__Version__ = 'v0.10'


def loadConfig():
	config = Tool.Config.ConfigIni('Config.ini')
	globals.G_CLIENT_IP = config.getKey('OrTClient','SERVER_IP')
	globals.G_CLIENT_PORT = config.getKeyInt('OrTClient','LISTEN_PORT')
	globals.G_CLIENT_CONNECT_MAXNUMBER = config.getKeyInt('OrTClient','CONNECT_MAXNUMBER')
	globals.G_CLIENT_LOGNAME = config.getKey('OrTClient','LOG_NAME')
	globals.G_CLIENT_LOGLEVEL = config.getKey('OrTClient','LOG_LEVEL')
	globals.G_SERVER_HOST = config.getKey('OrTClient','S_HOST')
	globals.G_SERVER_PORT = config.getKeyInt('OrTClient','S_PORT')
	globals.G_SECRET_KEY = config.getKeyInt('OrTClient','SECRET_KEY')

def logInit():
	globals.G_Log = Tool.Logger.getLogger(globals.G_CLIENT_LOGNAME)
	globals.G_Log.setLevel(globals.G_CLIENT_LOGLEVEL)

def init():
	loadConfig()
	logInit()

def main():
	print('This is Data Encryption Transmission System of OrTunnel.')
	print('(https://github.com/lixingke3650/OrTunnel)')
	print('OrTunnel Client Version: ' + __Version__)
	print('Python Version: ' + sys.version)
	print('')

	init()

	print('=====================================================')
	print('* Client IPAddr: %s' % globals.G_CLIENT_IP)
	print('* Client Port: %d' % globals.G_CLIENT_PORT)
	print('* Client C_Max: %d' % globals.G_CLIENT_CONNECT_MAXNUMBER)
	print('* Server Host: %s' % globals.G_SERVER_HOST)
	print('* Server Port: %d' % globals.G_SERVER_PORT)
	print('* Client Log Level: %s' % globals.G_Log.getLevel())
	print('=====================================================')
	print('')


if __name__ == '__main__':
    main()