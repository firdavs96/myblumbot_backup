# -*-coding: utf-8 -*-

import shelve
import config


class Shelver:
	conn = None
	
	def __init__(self, shelve_name=config.shelve_name):
		self.conn = shelve.open(shelve_name, writeback=True)
	
	def close(self):
		self.conn.close()
	
	def __enter__(self):
		return self
	
	def __exit__(self, Type, Value, Trace):
		self.close()
	
	def clear_shelve(self, shelve_name=None):
		for i in self.conn:
			print(i, ":", self.conn[i])
			del self.conn[i]
		print("shelve cleared")
	
	def show_shelve(self):
		for i in self.conn:
			print(i, ":", self.conn[i])

