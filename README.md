# OrTunnel  
  
实现数据加密在网络上传输的系统。  
可选加密方式：  

* ARC4流加密方式(利用PyCrypto实现)  
* SSL/TLS(TLSv1)  
  
关于SSL证书的使用：  

cert文件夹中提供的证书可以用作测试，  
同时给出了私钥，安全性无法得到保证，  
所以** 请另行制作私钥与证书，替换原文件。**  
  
附OpenSSL制作证书方法：  

>$ openssl genrsa 2048 > server.key  
>$ openssl req -new -key server.key > server.csr  
>$ openssl x509 -days 3650 -req -signkey server.key < server.csr > server.crt  
  

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
  
  