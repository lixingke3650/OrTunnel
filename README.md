# OrTunnel  
  
实现数据加密在网络上传输。  

启动例：  

* python3 ortunnel.py --config sample_server.conf  
  

可选加密方式：  

* ARC4流加密方式  
* 　　(v0.22版本前利用PyCrypto实现,新版本内部实现。详见Tool/Crypt.py)  
* SSL/TLS(TLSv1)  
  
关于SSL证书的使用：  

cert文件夹中提供的证书可以用作测试，  
因同时给出了私钥，安全性无法得到保证，  
所以使用时 **请另行制作私钥与证书，替换原文件。**  
  
附OpenSSL制作证书方法：  

>$ openssl genrsa 2048 > server.key  
>$ openssl req -new -key server.key > server.csr  
>$ openssl x509 -days 3650 -req -signkey server.key < server.csr > server.crt  
  
----  
### 更新至版本v0.44  

更新STL版本至PROTOCOL_TLS。  
更新Logger模块，加入调用方信息。  
  
2020.12.27  

----  
### 更新至版本v0.43  

修正MAC/Linux下socket释放不彻底的问题。

2018.07.01  

----  
### 更新至版本v0.42  

UDP发包间隔追加(一定程度防丢包)

2018.02.13

----  
### 更新至版本v0.41  

文件结构调整  
log修正  

2018.01.03  

----  
### 更新至版本v0.40  

客户端<->服务端通信UDP支持(UDP目前仅支持ARC4加密)  
文件结构调整  
Client与Server共用一个启动程序  
增加 --config 启动参数，载入配置文件  

2017.12.29  

----  
### 更新至版本v0.30  
  
可建立多条隧道 客户端/服务端请同时更新至0.30版  
ARC4模式下数据传输效率改善  
  
2017.09.25  

----  
### 更新至版本v0.25  
  
适用于Python3 (Python2请使用上一个稳定版0.24)  
ARC4更新为string和bytes两种加解密方式，密钥改为只接受bytes类型  
  
2016.5.12  

----  
### 更新至版本v0.24  
  
删除了不必要的日志信息  
控制台只在DEBUG下有输出    
  
2015.05.19  

----  
### 更新至版本v0.23  
  
解决ARC4加解密乱码问题  
内部实现ARC4加解密，不再需要依赖PyCrypto  
  
2015.02.28  
  
----
### 更新至版本v0.22  
  
加入SSL通信方式  
可能存在多个客户端连接一个服务器的情况，  
所以目前服务端不验证客户端证书。  
但从安全性角度考虑，可能会加入双方验证。  
*ARC4加密方式仍然会随机出现乱码，调查中。  
  
2015.02.25  
  
----
### 更新至版本v0.20  
  
加入ARC4数据流加密功能  
但偶尔会出现乱码，原因调查中。  
  
----  
### 更新至版本v0.10   
  
客户端与服务端稳定工作  
暂未加入数据流加密解密  
  
2015.02.19  
  
  
