#! /usr/bin/python3
# -*-coding: utf-8-*-
# FileName: ortunnel.py

# std
import platform
import sys
import argparse

# orignal
import globals
from Tool import *
import Server
import Client

# 版本说明
# 0.10: 基本功能实现
# 0.20: 追加加密解密功能
# 0.23: 追加连接测试功能
# 0.24: 删除无用的日志信息，控制台输出只在DEBUG时出现
# 0.25: 适用于Python3 (Python2请使用上一个稳定版0.24)
#       ARC4更新为string和bytes两种加解密方式，密钥改为只接受bytes类型
# 0.30: 可建立多条隧道 客户端/服务端请同时更新至0.30版
#       ARC4模式下数据传输效率改善
# 0.40: 客户端<->服务端通信UDP支持(UDP目前仅支持ARC4加密)
#       文件结构调整
#       Client与Server共用一个启动程序
#       增加 --config 启动参数，载入配置文件
# 0.41: 文件结构调整/log修正
# 0.42: UDP发包间隔追加(一定程度防丢包)
# 0.43: 修正MAC/Linux下socket释放不彻底的问题

__Version__ = 'v0.42'


OrTunnelService = None

def run_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    args = parser.parse_args()
    if (args.config != None):
        globals.G_CONFIG_FILE = args.config

def loadConfig():
    config = Config.ConfigIni(globals.G_CONFIG_FILE)
    globals.G_MODE = config.getKey('System','WORK_MODE')
    globals.G_LOG_NAME = config.getKey('System','LOG_NAME')
    globals.G_LOG_LEVEL = config.getKey('System','LOG_LEVEL')
    globals.G_SECRET_KEY = config.getKey('System','SECRET_KEY').encode('utf8')
    globals.G_SECRET_FLAG = config.getKeyBool('System','SECRET_FLAG')
    globals.G_SECRET_TYPE = config.getKey('System','SECRET_TYPE')
    if globals.G_SECRET_TYPE == 'TLS':
        globals.G_SECRET_TYPE = 'SSL'
    globals.G_TLS_CERT = config.getKey('System','SSL_CERT')
    globals.G_TLS_KEY = config.getKey('System','SSL_KEY')
    globals.G_TLS_CERT_VERIFY = config.getKey('System','SSL_CERT_VERIFY')
    globals.G_TUNNEL_METHOD = config.getKey('System','TUNNEL_METHOD')
    globals.G_TUNNEL_NUM = config.getKeyInt('System','TUNNEL_NUM')
    globals.G_TUNNEL_GROUP_INFO = []
    for i in range(globals.G_TUNNEL_NUM):
        globals.G_TUNNEL_GROUP_INFO.append((config.getKey('Tunnel'+str(i+1),'APP_METHOD'), \
                                            config.getKey('Tunnel'+str(i+1),'LISTEN_IP'), \
                                            config.getKeyInt('Tunnel'+str(i+1),'LISTEN_PORT'), \
                                            config.getKey('Tunnel'+str(i+1),'TARGET_HOST'), \
                                            config.getKeyInt('Tunnel'+str(i+1),'TARGET_PORT')))

    globals.G_LISTEN_CONNECT_HOLDMAX = config.getKeyInt('System','CONNECT_HOLDMAX')

def globalsInit():
    globals.G_Log = Logger.getLogger(globals.G_LOG_NAME, globals.G_MODE)
    globals.G_Log.setLevel(globals.G_LOG_LEVEL)

def init():
    loadConfig()
    globalsInit()

def start():
    global OrTunnelService
    if (globals.G_MODE == 'server'):
        OrTunnelService = Server.TunnelService()
        return OrTunnelService.start()
    elif (globals.G_MODE == 'client'):
        OrTunnelService = Client.TunnelService()
        return OrTunnelService.start()
    else:
        return False

def test():
    global OrTunnelService
    if (globals.G_MODE == 'client'):
        ret = OrTunnelService.testing()
        IO.printX('service test: %s' %ret)
    return

def ortunnel_main():
    IO.printX('OrTunnel (https://github.com/lixingke3650/OrTunnel)')
    IO.printX('Version: ' + __Version__)
    IO.printX('Python Version: %s (%s, %s)' %(platform.python_version(),platform.architecture()[0],platform.system()))
    IO.printX('')

    init()

    IO.printX('============================================================')
    IO.printX('* OrTunnel Mode: %s' % globals.G_MODE)
    IO.printX('* Network Method: %s' % globals.G_TUNNEL_METHOD)
    IO.printX('* Secret : %s' % globals.G_SECRET_FLAG)
    IO.printX('* Secret Type: %s' % globals.G_SECRET_TYPE)
    IO.printX('* Server Log Level: %s' % globals.G_Log.getLevel())

    for i in range(globals.G_TUNNEL_NUM):
        IO.printX('* Tunnel'+str(i+1))
        IO.printX('*   [listen] %s:%d <==> [target] %s:%d' \
            % (globals.G_TUNNEL_GROUP_INFO[i][globals.GD_LISTENIP], \
                globals.G_TUNNEL_GROUP_INFO[i][globals.GD_LISTENPORT], \
                globals.G_TUNNEL_GROUP_INFO[i][globals.GD_TARGETIP], \
                globals.G_TUNNEL_GROUP_INFO[i][globals.GD_TARGETPORT]))
    IO.printX('============================================================')
    IO.printX('')

    if (start() != True):
        IO.printX('OrTunnel Service Start Failed.')
        return

    # test
    test()

    IO.printX('OrTunnel Service Started.')
    IO.printX('')

if __name__ == '__main__':
    run_argparse()
    ortunnel_main()
