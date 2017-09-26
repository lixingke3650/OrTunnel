#! C:\Python\Python3\python
# -*-coding: utf-8-*-
# FileName: OrTClient.py

# std
import platform

# orignal
import globals
# from globals import G_Log
# import Tool
from Tool import *
from Client import *

# 版本说明
# 0.10: 基本功能实现
# 0.20: 追加加密解密功能
# 0.23: 追加连接测试功能
# 0.24: 删除无用的日志信息，控制台输出只在DEBUG时出现
# 0.25: 适用于Python3 (Python2请使用上一个稳定版0.24)
#       ARC4更新为string和bytes两种加解密方式，密钥改为只接受bytes类型
# 0.30: 可建立多条隧道 客户端/服务端请同时更新至0.30版
#       ARC4模式下数据传输效率改善
__Version__ = 'v0.30'


def loadConfig():
    config = Config.ConfigIni('config_client.ini')
    globals.G_LOG_NAME = config.getKey('OrTClient','LOG_NAME')
    globals.G_LOG_LEVEL = config.getKey('OrTClient','LOG_LEVEL')
    globals.G_SECRET_KEY = config.getKey('OrTClient','SECRET_KEY').encode('utf8')
    globals.G_SECRET_FLAG = config.getKeyBool('OrTClient','SECRET_FLAG')
    globals.G_SECRET_TYPE = config.getKey('OrTClient','SECRET_TYPE')
    if globals.G_SECRET_TYPE == 'TLS':
        globals.G_SECRET_TYPE = 'SSL'
    globals.G_TLS_CERT = config.getKey('OrTClient','SSL_CERT')
    globals.G_TLS_KEY = config.getKey('OrTClient','SSL_KEY')
    globals.G_TLS_CERT_VERIFY = config.getKey('OrTClient','SSL_CERT_VERIFY')
    globals.G_TUNNEL_NUM = config.getKeyInt('OrTClient','TUNNEL_NUM')
    globals.G_TUNNEL_GROUP_LIST = []
    for i in range(globals.G_TUNNEL_NUM):
        globals.G_TUNNEL_GROUP_LIST.append((config.getKey('Client'+str(i+1),'LISTEN_IP'), \
                                            config.getKeyInt('Client'+str(i+1),'LISTEN_PORT'), \
                                            config.getKey('Client'+str(i+1),'S_HOST'), \
                                            config.getKeyInt('Client'+str(i+1),'S_PORT')))
    globals.G_LISTEN_CONNECT_HOLDMAX = config.getKeyInt('OrTClient','CONNECT_HOLDMAX')

def globalsInit():
    globals.G_Log = Logger.getLogger(globals.G_LOG_NAME)
    globals.G_Log.setLevel(globals.G_LOG_LEVEL)

def init():
    loadConfig()
    globalsInit()

def start():
    OrTunnelClient = TunnelService.TunnelService()
    # 测试
    if (OrTunnelClient.testing() != True):
        IO.printX('unable to connect to OrTunnel Server!')
        return False

    return OrTunnelClient.start()

def main():
    IO.printX('OrTunnel Client  (https://github.com/lixingke3650/OrTunnel)')
    IO.printX('Version: ' + __Version__)
    IO.printX('Python Version: %s (%s, %s)' %(platform.python_version(),platform.architecture()[0],platform.system()))
    IO.printX('')

    init()

    IO.printX('============================================================')
    IO.printX('* Client Log Level: %s' % globals.G_Log.getLevel())
    IO.printX('* Secret: %s' % globals.G_SECRET_FLAG)
    IO.printX('* Secret Type: %s' % globals.G_SECRET_TYPE)

    for i in range(globals.G_TUNNEL_NUM):
        IO.printX('* Tunnel'+str(i+1))
        IO.printX('*   [local] %s:%d <==> [remote] %s:%d' \
            % (globals.G_TUNNEL_GROUP_LIST[i][0], \
                globals.G_TUNNEL_GROUP_LIST[i][1], \
                globals.G_TUNNEL_GROUP_LIST[i][2], \
                globals.G_TUNNEL_GROUP_LIST[i][3]))
    IO.printX('============================================================')
    IO.printX('')

    if (start() != True):
        IO.printX('OrTunnel Client Service Start Failed.')
        return

    IO.printX('OrTunnel Client Service Started.')
    IO.printX('')


if __name__ == '__main__':
    main()