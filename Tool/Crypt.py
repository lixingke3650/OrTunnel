#! C:\Python\Python2\python
# -*-coding: utf-8-*-
# FileName: Crypt.py

# std
import Crypto.Cipher.ARC4

# orignal


class CrypterARC4():
	"""加密解密类 - ARC4"""

	# _Key = None
	_Cipher_En = None
	_Cipher_De = None

	def __init__(self, key = b'O1r2T3u4n5n6e7l8'):
		# self._Key = key
		self._Cipher_En = Crypto.Cipher.ARC4.new(key)
		self._Cipher_De = Crypto.Cipher.ARC4.new(key)

	def enCrypt(self, buffer = ''):
		return self._Cipher_En.encrypt(buffer)

	def deCrypt(self, buffer = ''):
		return self._Cipher_De.decrypt(buffer)

if __name__ == '__main__' :
	myCrypter = CrypterARC4()
	tmp = myCrypter.enCrypt('hello')
	print (myCrypter.deCrypt(tmp))




