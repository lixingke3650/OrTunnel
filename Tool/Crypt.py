#! C:\Python\Python3\python
# -*-coding: utf-8-*-
# FileName: Crypt.py

# std

# orignal

__all__ = ["CrypterARC4", "ARC4"]

class CrypterARC4():
    """加密解密类 - ARC4

    等长度数据加解密，使用enCryptB/deCryptB 要快
    b'hello?'类型的加密解密 enCryptB/deCryptB 要快
    'こんにちは?'类型的加密解密 enCryptStr/deCryptStr 要快 ('こんにちは?'转换为bytes后，长度加大)
    """

    _Cipher_En = None
    _Cipher_De = None

    def __init__(self, key = b'O1r2T3u4n5n6e7l8'):
        if (type(key) != bytes):
            raise TypeError("key must is bytes!")
        self._Cipher_En = ARC4(key)
        self._Cipher_De = ARC4(key)

    def enCrypt(self, buffer = b''):
        '''bytes加密'''
        return self._Cipher_En.encrypt(buffer)

    def deCrypt(self, buffer = b''):
        '''bytes解密'''
        return self._Cipher_De.decrypt(buffer)

    def enCryptB(self, buffer = b''):
        return self.enCrypt(buffer)

    def deCryptB(self, buffer = b''):
        return self.deCrypt(buffer)

    def enCryptStr(self, buffer = ''):
        return self._Cipher_En.encryptstr(buffer)

    def deCryptStr(self, buffer = ''):
        return self._Cipher_De.decryptstr(buffer)

class ARC4():
    '''ARC4 加解密
    实例化后调用encrypt，decrypt会节省SBox初始化时间，
    但因为加解密过程中SBox是动态的，若加解密不同数据请申请不同的实例。

    原理: 异或的异或等于原有数据。即 A xor B = C, C xor B = A
          当B未知时，很难从C中获取A。

    优点: 速度快，算法实现简单，加密性较好。

    不足: 1.属于对称加密，即加密解密使用同一key，不利于key的保管。
        2.加密用的B是根据key生成的伪随机序列。伪随机即序列中字符出现的概率是不同的，
        用这种伪随机序列异或得到的加密数据就变得有迹可循。
        具体可参考下面的文章或讲稿：
        《A Practical Attack on Broadcast RC4》 - Itsik Mantin and Adi Shamir
        《On the Security of RC4 in TLS》 - Nadhem AlFardan, Dan Bernstein, Kenny Paterson, Bertram Poettering,
Jacob Schuldt

    步骤: 1.由明文密钥key生成256位的加密用密钥(又称伪随机数，即B)
        2.将待加密数据与B异或，得到加密数据
        3.解密端重复上述步骤即可获取原数据
    '''

    _Key = None
    _KeyLen = None
    _SBox = None
    _SBoxLen = 256

    def __init__(self, key):
        self._Key = key
        self._KeyLen = len(self._Key)
        self.initSBox()
        self._I = 0
        self._J = 0

    def initSBox(self):
        '''SBox初始化'''

        # self._SBox = range(self._SBoxLen) # PY2
        self._SBox = list(range(self._SBoxLen))
        j = 0
        # for i in xrange(self._SBoxLen): # PY2
        for i in range(self._SBoxLen):
            # j = (j + self._SBox[i] + ord(self._Key[i % self._KeyLen])) % self._SBoxLen # str key
            j = (j + self._SBox[i] + self._Key[i % self._KeyLen]) % self._SBoxLen
            self._SBox[i], self._SBox[j] = self._SBox[j], self._SBox[i]

    def opergen(self):
        '''SBox中数据是随操作变化的，此处返回generator，用以与流数据作异或操作
        '''

        while True:
            self._I = (self._I + 1) % self._SBoxLen
            self._J = (self._J + self._SBox[self._I]) % self._SBoxLen
            self._SBox[self._I], self._SBox[self._J] = self._SBox[self._J], self._SBox[self._I]
            oper = self._SBox[(self._SBox[self._I] + self._SBox[self._J]) % self._SBoxLen]
            yield oper

    def gear(self, buffer):
        '''异或操作 buffer is bytes'''

        out = []
        for c in buffer:
            out.append(c ^ self.opergen().__next__())
        return bytes(out)

    def gearstr(self, buffer):
        '''异或操作 buffer is str'''

        out = []
        for c in buffer:
            out.append(chr(ord(c) ^ self.opergen().__next__()))
        return ''.join(out)

    def encrypt(self, buffer):
        '''加密函数 buffer is bytes'''

        return self.gear(buffer)

    def decrypt(self, buffer):
        '''解密函数 buffer is bytes'''

        return self.gear(buffer)

    def encryptstr(self, buffer):
        '''加密函数 buffer is str'''

        return self.gearstr(buffer)

    def decryptstr(self, buffer):
        '''解密函数 buffer is str'''

        return self.gearstr(buffer)

if __name__ == '__main__' :
    myCrypter = CrypterARC4(b'O1r2T3u4n5n6e7l8')
    tmp = myCrypter.enCrypt(b'hello?')
    print (myCrypter.deCrypt(tmp))

    # print(bytes([51, 13, 10]))
    # print(bytes('3', 'utf8') + b'\r\n')
    # n = 3
    # print(bytes(str(n), 'ascii') + b'\r\n')
