#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: OrTClient.py

# std
import sys

# orignal
import globals
from globals import G_Log
# import Tool
from Tool import *
import Client.TunnelService

# 版本说明
# 0.10：基本功能实现
__Version__ = 'v0.10'


def loadConfig():
	config = ConfigIni('Config.ini')
	globals.G_CLIENT_IP = config.getKey('OrTClient','SERVER_IP')
	globals.G_CLIENT_PORT = config.getKeyInt('OrTClient','LISTEN_PORT')
	globals.G_CLIENT_CONNECT_MAXNUMBER = config.getKeyInt('OrTClient','CONNECT_MAXNUMBER')
	globals.G_CLIENT_LOGNAME = config.getKey('OrTClient','LOG_NAME')
	globals.G_CLIENT_LOGLEVEL = config.getKey('OrTClient','LOG_LEVEL')
	globals.G_SERVER_HOST = config.getKey('OrTClient','S_HOST')
	globals.G_SERVER_PORT = config.getKeyInt('OrTClient','S_PORT')
	globals.G_SECRET_KEY = config.getKeyInt('OrTClient','SECRET_KEY')

def globalsInit():
	globals.G_Log = Logger.getLogger(globals.G_CLIENT_LOGNAME)
	globals.G_Log.setLevel(globals.G_CLIENT_LOGLEVEL)

def init():
	loadConfig()
	globalsInit()

def start():
	OrTunnelClient = Client.TunnelService.TunnelService()
	return OrTunnelClient.start()

def main():
	printX('This is Data Encryption Transmission System of OrTunnel.')
	printX('(https://github.com/lixingke3650/OrTunnel)')
	printX('OrTunnel Client Version: ' + __Version__)
	printX('Python Version: ' + sys.version)
	printX('')

	init()

	printX('=====================================================')
	printX('* Client IPAddr: %s' % globals.G_CLIENT_IP)
	printX('* Client Port: %d' % globals.G_CLIENT_PORT)
	# printX('* Client C_Max: %d' % globals.G_CLIENT_CONNECT_MAXNUMBER)
	printX('* Server Host: %s' % globals.G_SERVER_HOST)
	printX('* Server Port: %d' % globals.G_SERVER_PORT)
	printX('* Client Log Level: %s' % globals.G_Log.getLevel())
	printX('=====================================================')
	printX('')

	if (start() != True):
		printX('OrTunnel Client Service Start Failed.')
		return

	printX('OrTunnel Client Service Start OK.')
	printX('')


if __name__ == '__main__':
	main()