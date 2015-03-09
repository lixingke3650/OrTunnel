#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: OrTClient.py

# std
import platform

# orignal
import globals
from globals import G_Log
# import Tool
from Tool import *
import Client.TunnelService

# 版本说明
# 0.10：基本功能实现
# 0.20：追加加密解密功能
__Version__ = 'v0.23'


def loadConfig():
	config = ConfigIni('Config.ini')
	globals.G_LISTEN_IP = config.getKey('OrTClient','LISTEN_IP')
	globals.G_LISTEN_PORT = config.getKeyInt('OrTClient','LISTEN_PORT')
	globals.G_TARGET_HOST = config.getKey('OrTClient','S_HOST')
	globals.G_TARGET_PORT = config.getKeyInt('OrTClient','S_PORT')
	globals.G_LISTEN_CONNECT_MAXNUMBER = config.getKeyInt('OrTClient','CONNECT_MAXNUMBER')
	globals.G_LOGNAME = config.getKey('OrTClient','LOG_NAME')
	globals.G_LOGLEVEL = config.getKey('OrTClient','LOG_LEVEL')
	globals.G_SECRET_KEY = config.getKey('OrTClient','SECRET_KEY')
	globals.G_SECRET_FLAG = config.getKeyBool('OrTClient','SECRET_FLAG')
	globals.G_SECRET_TYPE = config.getKey('OrTClient','SECRET_TYPE')
	if globals.G_SECRET_TYPE == 'TLS':
		globals.G_SECRET_TYPE = 'SSL'
	globals.G_TLS_CERT = config.getKey('OrTClient','SSL_CERT')
	globals.G_TLS_KEY = config.getKey('OrTClient','SSL_KEY')
	globals.G_TLS_CERT_VERIFY = config.getKey('OrTClient','SSL_CERT_VERIFY')

def globalsInit():
	globals.G_Log = Logger.getLogger(globals.G_LOGNAME)
	globals.G_Log.setLevel(globals.G_LOGLEVEL)

def init():
	loadConfig()
	globalsInit()

def start():
	OrTunnelClient = Client.TunnelService.TunnelService()
	# 测试
	if (OrTunnelClient.testing() != True):
		printX('unable to connect to OrTunnel Server!')
		return False

	return OrTunnelClient.start()

def main():
	printX('OrTunnel Client  (https://github.com/lixingke3650/OrTunnel)')
	printX('Version: ' + __Version__)
	printX('Python Version: %s (%s, %s)' %(platform.python_version(),platform.architecture()[0],platform.system()))
	printX('')

	init()

	printX('============================================================')
	printX('* Client IPAddr: %s' % globals.G_LISTEN_IP)
	printX('* Client Port: %d' % globals.G_LISTEN_PORT)
	printX('* Server Host: %s' % globals.G_TARGET_HOST)
	printX('* Server Port: %d' % globals.G_TARGET_PORT)
	printX('* Secret Flag: %s' % globals.G_SECRET_FLAG)
	printX('* Secret Type: %s' % globals.G_SECRET_TYPE)
	printX('* Client Log Level: %s' % globals.G_Log.getLevel())
	printX('============================================================')
	printX('')

	if (start() != True):
		printX('OrTunnel Client Service Start Failed.')
		raw_input()
		return

	printX('OrTunnel Client Service Start OK.')
	printX('')


if __name__ == '__main__':
	main()