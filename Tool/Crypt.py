#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: Crypt.py

# std
# import Crypto.Cipher.ARC4

# orignal


__all__ = ["CrypterARC4", "ARC4"]

class CrypterARC4():
	"""加密解密类 - ARC4"""

	_Cipher_En = None
	_Cipher_De = None

	def __init__(self, key = b'O1r2T3u4n5n6e7l8'):
		# self._Cipher_En = Crypto.Cipher.ARC4.new(key)
		# self._Cipher_De = Crypto.Cipher.ARC4.new(key)
		self._Cipher_En = ARC4(key)
		self._Cipher_De = ARC4(key)

	def enCrypt(self, buffer = b''):
		return self._Cipher_En.encrypt(buffer)

	def deCrypt(self, buffer = b''):
		return self._Cipher_De.decrypt(buffer)

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

	def __init__(self, key = b'0123456789ABCDEF'):
		self._Key = key
		self._KeyLen = len(self._Key)
		self.initSBox()
		self._I = 0
		self._J = 0

	def initSBox(self):
		self._SBox = range(self._SBoxLen)
		j = 0
		for i in xrange(self._SBoxLen):
			j = (j + self._SBox[i] + ord(self._Key[i % self._KeyLen])) % self._SBoxLen
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
		'''异或操作'''

		out = []
		for c in buffer:
			out.append(chr(ord(c) ^ self.opergen().next()))
		return ''.join(out)

	def encrypt(self, buffer):
		'''加密函数'''

		return self.gear(buffer)

	def decrypt(self, buffer):
		'''解密函数'''

		return self.gear(buffer)

if __name__ == '__main__' :
	myCrypter = CrypterARC4()
	tmp = myCrypter.enCrypt('hello')
	print (myCrypter.deCrypt(tmp))

	en = ARC4()
	de = ARC4()
	tmp = en.gear('how are you today?')
	print (de.gear(tmp))


