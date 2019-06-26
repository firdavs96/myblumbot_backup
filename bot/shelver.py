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

	# TODO Test this func
	def clear_shelve(self, shelve_name=None):
		if shelve_name:
			with self.__init__(shelve_name=shelve_name).conn as states:
				for i in states:
					print(i, ":", states[i])
					del states[i]
		else:
			with self.__init__().conn as states:
				for i in states:
					print(i, ":", states[i])
					del states[i]
