# -*-coding: utf-8 -*-

import shelve
import bot.config as config


class Shelver(object):
	def __init__(self, shelve_name=None):
		shelve_name = shelve_name or config.shelve_name
		self.conn = shelve.open(shelve_name, writeback=True)

	def close(self):
		self.conn.close()

	def __enter__(self):
		return self

	def __exit__(self, Type, Value, Trace):
		self.close()

	def clear_shelve(self, shelve_name=None):
		with self.__init__(shelve_name).conn as states:
			for i in states:
				print(i, ":", states[i])
				del states[i]
