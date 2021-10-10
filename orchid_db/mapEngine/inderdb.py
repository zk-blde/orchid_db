from .base import BaseMapWrapper
import binascii,base64

class inder_db(BaseMapWrapper):

	'''
	用户提示:
	需要输入的格式如下 :
	methed   您的具体操作
	[key]    您要操作的键
	[value]  您要操作的值
	Available Commands: SET set a key to db GET get a key from db UPDATE update key DELETE delete key
	'''
	def __init__(self):
		self.lst_key = []
		self.lst_value = []

	def help(self):
		return self.__doc__

	def __call__(self, key):
		return self.get(key)

	# 十六进制转换为字符
	def hex2char(self, data):
		#    binascii.a2b_hex(hexstr)
		output = binascii.unhexlify(data)
		ori_data = base64.b64decode(output).decode()
		# print(ori_data)
		return ori_data

	# 字符转换为十六进制
	def char2hex(self, data):
		# data = b'data'
		#    binascii.b2a_hex(data)
		b = base64.b64encode(data.encode())
		output = binascii.hexlify(b)
		# print(output)
		return output


	# 这里添加二分查找
	def _binary_search(self,li, val):
		left = 0
		right = len(li) - 1
		while left <= right:
			mid = (left + right) // 2
			if li[mid] == val:
				return mid
			elif li[mid] > val:
				right = mid - 1
			else:
				left = mid + 1
		else:
			return None

	# 二分法
	def _binary_search_two(self, li, val):
		left = 0
		right = len(li) - 1
		while left <= right:
			mid = (left + right) // 2
			if li[mid] > val:
				right = mid - 1
			else:
				left = mid + 1
		else:
			return right

	def __getitem__(self,item):
		try:
			item = self.char2hex(item)
			mid = self._binary_search(self.lst_key,item)
			return self.hex2char(self.lst_value[mid])
		except:
			raise Exception("This key is not find")

	def __setitem__(self, key, value):
		key = self.char2hex(key)
		value = self.char2hex(value)
		# 调用二分法,检测key 值有没有在列表
		mid = self._binary_search(self.lst_key,key)
		#print(mid)
		# 没有在的情况
		if mid == None:
			# 调用半截二分法
			num = self._binary_search_two(self.lst_key,key)
			self.lst_key.insert(num,key)
			self.lst_value.insert(num,value)
		# 在的情况
		else:
			#print(1)
			self.lst_key[mid] = key
			self.lst_value[mid] = value

	def __delitem__(self, key):
		key = self.char2hex(key)
		try:
			mid = self._binary_search(self.lst_key, key)
			# print(mid,11111)
			# 如果 有 key 值,直接删除 , 对应的键值也删除
			if mid != None:
				self.lst_key.pop(mid)
				self.lst_value.pop(mid)
		except:
			raise Exception("This key is not find")

	def get(self, key):
		key = self.char2hex(key)
		mid = self._binary_search(self.lst_key, key)
		try:
			data=self.lst_value[mid]
		except:
			return None
		return self.hex2char(data)


	def _del(self, key):
		key = self.char2hex(key)
		try:
			mid = self._binary_search(self.lst_key, key)
			# 如果 有 key 值,直接删除 , 对应的键值也删除
			if mid != None:
				self.lst_key.pop(mid)
				self.lst_value.pop(mid)

		except:
			raise Exception("please implementation")

	def pop(self, key):
		assert type(key) == str
		key = self.char2hex(key)
		return self._del(key)

# obj = inder_db()
#
# obj["key1"] = "value2"
# obj["key1"] = "value"
# obj["key1"] = "value5"
# del obj["key1"]
# print(obj.lst_key,obj.lst_value)
# print(obj["key"])