# -*-coding: utf-8 -*-
from myblumbot.sqlighter import SQLighter
from myblumbot.shelver import Shelver
import myblumbot.config as config
from myblumbot.config import shelve_name
import time
import myblumbot.excel as excel


def get_fullname_username(message) -> (str, str):
	fullname = message.from_user.first_name
	if message.from_user.last_name is not None:
		fullname += " " + message.from_user.last_name

	username = "" if message.from_user.username is None else message.from_user.username
	return fullname, username


def get_lang(uid):
	with SQLighter() as db:
		return db.get_lang(uid)


def state(uid):
	with Shelver() as states:
		if uid in states.conn:
			try:
				return states.conn[uid]['cur']
			except KeyError:
				return None
		else:
			return None


def path(uid):
	with Shelver().conn as states:
		if uid in states:
			try:
				return states[uid]['path']
			except:
				return None
		else:
			return None


def compute_height(aventos, *args):
	if aventos == 'AVENTOS HF':
		height = args[0]
		return int(height * 0.3 - 57)


def compute_x_y(aventos, a, b, c, d, e, f, lever_value=None):
	if aventos == 'AVENTOS HF':
		x = e / 2 + 47
		y = d - (c - f) / 2 + 12.5
		return x, y

	if aventos == 'AVENTOS HS':
		x = (d - (b - e) / 2) + 196.5
		y = (d - (c - f) / 2) + 12.5
		return x, y

	if aventos == 'AVENTOS HL':
		if lever_value is None:
			raise Exception("Need correct lever value for HL mechnism")
		for i in lever_value:
			if i not in config.hl_lever_values_for_x_y.values():
				raise Exception("Need correct lever value for HL mechnism")

		lever_values = lever_value
		x = [d - (b - e) / 2 + lever_value for lever_value in lever_values]
		y = [(d - (c - f) / 2) + 12.5 for _ in range(len(x))]
		return x, y

	if aventos == 'AVENTOS HK top':
		x = 69 - (b - e) / 2
		y = d - (c - f) / 2 + 12.5
		return x, y

	if aventos == 'AVENTOS HK-S':
		x = 78 - (b - e) / 2
		y = d - (c - f) / 2 + 12.5
		return x, y

	if aventos == 'AVENTOS HK-XS':
		x = [d - (b - e) / 2 + i for i in [125.5, 135, 143.5]]
		y = d - (c - f) / 2 + 15.5
		return x, y

	if aventos == 'AVENTOS HK-XS TIP-ON':
		x = [d - (b - e) / 2 + i for i in [125.5, 135, 143.5]]
		y = d - (c - f) / 2 + 15.5
		return x, y


def log(uid, text, func_name=None):
	if not func_name:
		print(str(time.strftime("%c | uid: ")) + str(uid) + " | state: " + str(state(uid)) + " | text: " + str(text))
	else:
		print(str(time.strftime("%c | uid: ")) + str(uid) + " | state: " + str(state(uid)) + " | text: " + str(text) \
			  + " | in_function: " + func_name)


def get_recomendation_mechanism(coef, aventos, height=None):
	with SQLighter() as db:
		if aventos in config.mechanism_with_height_parameter:
			if height is not None:
				return db.get_recomendation_mechanism_hs_hl(height, coef, aventos)
			else:
				raise Exception('Need Height parameter')
		else:
			return db.get_recomendation_mechanism(coef, aventos)


def round_height(height):
	if height % 10 == 0:
		return height
	elif height % 5 == 0:
		return height
	elif height % 10 == 6 and height // 10 in (67, 52):
		return height
	else:
		last_digit = height % 10
		first_two_digit = height // 10
		if first_two_digit in (67, 52) and last_digit in (7, 8):
			last_digit = 6
		elif last_digit in (9, 8):
			first_two_digit += 1
			last_digit = 0
		elif last_digit in (7, 6, 4, 3):
			last_digit = 5
		elif last_digit in (2, 1):
			last_digit = 0

		return int(str(first_two_digit) + str(last_digit))


def is_in_catalog(product, lang):
	if lang not in config.languages:
		return False
	with SQLighter() as db:
		return product in db.get_products(lang)


def get_type_in_states(states):
	for type in config.posting_file_types:
		if type in states:
			return type
	return None


def user_blocked_bot(uid):
	with SQLighter() as db:
		db.user_blocked_bot(uid)


def user_unblocked_bot(uid):
	with SQLighter() as db:
		db.user_unblocked_bot(uid)
