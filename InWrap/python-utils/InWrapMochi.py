import sys
import socket
import hashlib
from pymargo.core import Engine
from pysdskv.client import *
import matplotlib.pyplot as plt
import numpy as np
import random 

class InWrapMochi:

	def __init__(self, transport, address, p_id, db_n):
		self.engine = Engine(transport)
		self.server_addr = address
		self.provider_id = p_id
		self.db_name = db_n

		# init the engine
		self.client = SDSKVClient(self.engine)
		self.addr = self.engine.lookup(self.server_addr)
		self.provider_handle = self.client.create_provider_handle(self.addr, self.provider_id)
		self.db = self.provider_handle.open(self.db_name)

		# create a dictionary for values
		self.command_dic = {}
		self.used_unique_ids = []
		self.count = 0

		self.addingKeys = False



	def put_keyval(self, key, val):
		self.db.put(key, val)


	def del_key(self, key):
		if (self.db.exists(key)):
			self.db.erase(key)
		else:
			return "key does not exist"


	def get_val(self, key):
		if (self.db.exists(key)):
			return self.db.get(key)
		else:
			return "key does not exist"


	def exists(self, key):
		return self.db.exists(key)


	def list_keyVal(self):
		key,val = self.db.list_keyvals()
		return key,val


	def shutdown(self):
		self.client.shutdown_service(self.addr)



	def getIP(self):
		hostname = socket.gethostname()    
		IPAddr = socket.gethostbyname(hostname)  
		return str(IPAddr)


	def generateHash(self, value):
		hash_object = hashlib.md5(value.encode())
		temp_str = str(hash_object.hexdigest())
		return ( temp_str[0:8] )


	# Transaction operations: Set and commit
	def set(self, key, value):
		self.command_dic[key + "-" + str(self.count)] = value
		self.count = self.count + 1


	def commit(self):

		ip_addr = self.getIP()
		hash_val = self.generateHash(ip_addr)
		new_key = "NEW_KEY_" + hash_val

		# Loop until you can add a new key
		while ( self.db.exists(new_key) ): 
			continue


		# Generate a random number to pad keys with
		#rand_num = random.randint(99999,1000000)
		#while rand_num in self.used_unique_ids:
		#	rand_num = random.randint(99999,1000000)

		#self.used_unique_ids.append(rand_num)

		# Format of keys:
		# XXXXXX:Key-YYY

		# Add keys to mochi DB
		key_list = []
		self.addingKeys = True
		#self.db.put("NEW_KEY", "0")	# adding keys
		for key,val in self.command_dic.items():
			key_padded = hash_val + ":" + key	# add unique tag to each
			#key_padded = key + ":" + str(rand_num)	# add unique tag to each
			self.db.put(key_padded, val)			# put key in mochi db

			key_list.append(key)	# save the key for later deletion

			print("key: ", key_padded)
			print("val: ", val)

		#self.db.put("NEW_KEY", str(rand_num))	# adding keys done
		self.db.put(new_key, hash_val)	# adding keys done
		self.addingKeys = False

		# Delete keys
		for k in key_list:
			del self.command_dic[k]




# Run:
"""
import sys
sys.path.insert(1, '/home/pascal/projects/InWrap/python-utils')
import InWrapMochi
conn = InWrapMochi.InWrapMochi("na+sm","na+sm://2584/0",1,"foo")

Darwin:
import sys
sys.path.insert(1,'/projects/insituperf/InWrap/InWrap/python-utils')
import InWrapMochi
conn = InWrapMochi.InWrapMochi("ofi+tcp","ofi+tcp://192.168.101.184:1234",1,"struc1")
"""