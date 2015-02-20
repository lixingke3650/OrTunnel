#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: OrTServer.py

# std
import sys

# orignal
import globals
from globals import G_Log
# import Tool
from Tool import *
import Server.TunnelService

# 版本说明
# 0.10：基本功能实现
# 0.20：追加加密解密功能
__Version__ = 'v0.21'


def loadConfig():
	config = ConfigIni('Config.ini')
	globals.G_LISTEN_IP = config.getKey('OrTServer','LISTEN_IP')
	globals.G_LISTEN_PORT = config.getKeyInt('OrTServer','LISTEN_PORT')
	globals.G_LISTEN_CONNECT_MAXNUMBER = config.getKeyInt('OrTServer','CONNECT_MAXNUMBER')
	globals.G_APP_HOST = config.getKey('OrTServer','APP_HOST')
	globals.G_APP_PORT = config.getKeyInt('OrTServer','APP_PORT')
	globals.G_LOGNAME = config.getKey('OrTServer','LOG_NAME')
	globals.G_LOGLEVEL = config.getKey('OrTServer','LOG_LEVEL')
	globals.G_SECRET_KEY = config.getKey('OrTServer','SECRET_KEY')
	globals.G_SECRET_FLAG = config.getKeyBool('OrTServer','SECRET_FLAG')

def globalsInit():
	globals.G_Log = Logger.getLogger(globals.G_LOGNAME)
	globals.G_Log.setLevel(globals.G_LOGLEVEL)

def init():
	loadConfig()
	globalsInit()

def start():
	OrTunnelServer = Server.TunnelService.TunnelService()
	return OrTunnelServer.start()

def main():
	printX('This is Data Encryption Transmission System of OrTunnel.')
	printX('(https://github.com/lixingke3650/OrTunnel)')
	printX('OrTunnel Server Version: ' + __Version__)
	printX('Python Version: ' + sys.version)
	printX('')

	init()

	printX('=====================================================')
	printX('* Listen IPAddr: %s' % globals.G_LISTEN_IP)
	printX('* Listen Port: %d' % globals.G_LISTEN_PORT)
	printX('* Target App Host: %s' % globals.G_APP_HOST)
	printX('* Target App Port: %d' % globals.G_APP_PORT)
	printX('* Secret Flag: %s' % globals.G_SECRET_FLAG)
	printX('* Server Log Level: %s' % globals.G_Log.getLevel())
	printX('=====================================================')
	printX('')

	if (start() != True):
		printX('OrTunnel Server Service Start Failed.')
		return

	printX('OrTunnel Server Service Start OK.')
	printX('')


if __name__ == '__main__':
	main()