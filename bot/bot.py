# -*-coding: utf-8 -*-

import config
import telebot
from shelver import Shelver
import utils
from utils import state
from utils import log
from markup import markup
from sqlighter import SQLighter
import cherrypy
import sys
import excel
import os
from threading import Thread
import time

bot = telebot.TeleBot(config.token)


def post(messages, user_list):
	print("Рассылка начата")
	for uid in user_list:
		try:
			for message in messages:
				if message.text:
					bot.send_message(uid, message.text, parse_mode='HTML', disable_notification=True)
				if message.location:
					bot.send_location(uid, message.location.latitude, message.location.longitude,
									  disable_notification=True)
				if message.sticker:
					bot.send_sticker(uid, message.sticker.file_id, disable_notification=True)
				if message.document:
					bot.send_document(uid, message.document.file_id, caption=message.caption, disable_notification=True)
				if message.photo:
					bot.send_photo(uid, message.photo[0].file_id, caption=message.caption, disable_notification=True)
				if message.video:
					bot.send_video(uid, message.video.file_id, caption=message.caption, disable_notification=True)
				if message.audio:
					bot.send_audio(uid, message.audio.file_id, caption=message.caption, disable_notification=True)
			utils.user_unblocked_bot(uid)
		except Exception as e:
			print("Exception in post func: ", e)
			utils.user_blocked_bot(uid)
		time.sleep(0.5)
	print("Рассылка закончена")


# *****************************************************************************************************
# *****************************************************************************************************

def send_error_and_change_state(bot, states, uid, db):
	text = "<b>⚠️ Произошла ошибка. Пожалуйста, повторите ввод параметров.</b>\n\n" \
		   "Если ошибка повторится, обратитесь к администраторам: {admins}".format(
		admins=", ".join(config.admin_nicknames)
	)
	m = markup(db, 'main_menu', lang=db.get_lang(uid))
	states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
	bot.send_message(uid, text, reply_markup=m, parse_mode="HTML")
	return


@bot.message_handler(func=lambda m: str(m.from_user.id) != '3235063' and config.TEST_CONFIG)
def fa(message):
	print(message.from_user.id, ' trying connect to bot')


#
# @bot.message_handler(content_types=['sticker'])
# def asd(message):
# 	print('Sticker')
# 	bot.send_sticker(message.from_user.id, message.sticker.file_id)
# 	bot.send_message(message.from_user.id, message.sticker.file_id)
# 	print(message.sticker.file_id)
#
# @bot.message_handler(content_types=['video'])
# def asd(message):
# 	print('Video')
# 	bot.send_video(message.from_user.id, message.video.file_id, caption=message.video.file_id)
# 	print(message.video.file_id)
#
# @bot.message_handler(content_types=['photo'])
# def asd(message):
# 	print('Photo')
# 	bot.send_photo(message.from_user.id, message.photo[0].file_id, caption=message.photo[0].file_id)
# 	print(message.photo[0].file_id)
#
# @bot.message_handler(content_types=['document'])
# def asd(message):
# 	print('Document')
# 	bot.send_document(message.from_user.id, message.document.file_id, caption=message.document.file_id)
# 	print(message.document.file_id)

# *****************************************************************************************************
# *****************************************************************************************************

@bot.message_handler(func=lambda m: SQLighter().is_banned(str(m.from_user.id))
									and not SQLighter().is_admin(str(m.from_user.id)))
def banned(message):
	uid = str(message.from_user.id)
	log(uid, message.text, func_name=sys._getframe().f_code.co_name)

	with SQLighter() as db:
		lang = db.get_lang(uid)
		admins = '\n'.join(config.admin_nicknames)
		text = db.get_message('you_banned_message', lang=lang).format(admins)
		m = markup(db, 'banned_markup')
		bot.send_message(uid, text, parse_mode='HTML', reply_markup=m)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO хэндлер на случай, если пользователя нету в состояних
@bot.message_handler(func=lambda m: str(m.from_user.id) not in Shelver().conn)
def first_handler(message):
	uid = str(message.from_user.id)
	log(uid, message.text, func_name=sys._getframe().f_code.co_name)

	with SQLighter() as db, Shelver().conn as states:
		if db.get_lang(uid) not in config.languages:
			states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
			first_name, user_name = utils.get_fullname_username(message)
			if not db.has_user(uid):
				db.save_user_info(uid, first_name, user_name)
			elif db.is_stopped_bot(uid):
				db.user_unblocked_bot(uid)

			m = markup(db, states[uid]['cur'])
			text = db.get_message(states[uid]['cur'])[0]
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif not db.has_phone(uid):
			lang = db.get_lang(uid)
			states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
			full_name, _ = utils.get_fullname_username(message)
			text = db.get_message(states[uid]['cur'], lang=lang).format(full_name)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		else:
			lang = db.get_lang(uid)
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, text, reply_markup=m)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Выводит меню языка
@bot.message_handler(func=lambda m: utils.get_lang(str(m.from_user.id)) not in config.languages
									and state(str(m.from_user.id)) != 'lang_menu')
def first_menu(message):
	uid = str(message.from_user.id)
	log(uid, message.text, func_name=sys._getframe().f_code.co_name)

	with SQLighter() as db, Shelver().conn as states:
		states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
		first_name, user_name = utils.get_fullname_username(message)
		if not db.has_user(uid):
			db.save_user_info(uid, first_name, user_name)
		elif db.is_stopped_bot(uid):
			db.user_unblocked_bot(uid)

		m = markup(db, states[uid]['cur'])
		text = db.get_message(states[uid]['cur'])[0]
		bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Меню выбора языка. Выводит запрос контакта.
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'lang_menu')
@bot.message_handler(func=lambda m: SQLighter().has_user(str(m.from_user.id))
									and not SQLighter().has_phone(str(m.from_user.id))
									and str(m.from_user.id) not in Shelver().conn)
def lang_menu(message):
	uid = str(message.from_user.id)
	log(uid, message.text, func_name=sys._getframe().f_code.co_name)

	with SQLighter() as db, Shelver().conn as states:
		if not db.has_user(uid):
			full_name, user_name = utils.get_fullname_username(message)
			db.save_user_info(uid, full_name, user_name)

		if db.is_stopped_bot(uid):
			db.user_unblocked_bot(uid)

		if message.text in db.get_buttons('lang_menu') and len(db.get_buttons('lang_menu')) == 2:
			if message.text == db.get_buttons('ru_lang')[0]:
				lang = 'ru'
			else:
				lang = 'uz'
			db.set_lang(uid, lang)
			if not db.has_phone(uid):
				states[uid]['cur'] = 'send_phone_menu'
				states[uid]['path'] = [states[uid]['cur']]
				full_name, _ = utils.get_fullname_username(message)
				text = db.get_message(states[uid]['cur'], lang=lang).format(full_name)
				m = markup(db, states[uid]['cur'], lang=lang)
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			else:
				states[uid]['cur'] = 'main_menu'
				states[uid]['path'] = ['main_menu']
				m = markup(db, states[uid]['cur'], lang=lang)
				text = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
				bot.send_sticker(uid, text, reply_markup=m)
		else:
			states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
			m = markup(db, states[uid]['cur'])
			text = db.get_message(states[uid]['cur'])[0]
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Меню отправки контакта. Выводит стартовое меню.
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'send_phone_menu', content_types=['text', 'contact'])
def phone_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		lang = db.get_lang(uid)

		if message.text and db.has_phone(uid):
			log(uid, message.text, func_name=sys._getframe().f_code.co_name)
			states[uid]['cur'] = 'main_menu'
			states[uid]['path'] = [states[uid]['cur']]
			m = markup(db, states[uid]['cur'], lang=lang)
			sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, sticker_id, reply_markup=m)
			return

		elif message.text and not db.has_phone(uid):
			log(uid, message.text, func_name=sys._getframe().f_code.co_name)
			states[uid]['cur'] = 'send_phone_menu'
			states[uid]['path'] = [states[uid]['cur']]
			text = db.get_message("wrong_contact", lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			return

		else:
			log(uid, "phone: +" + message.contact.phone_number)
			if not db.has_user(uid) or db.get_lang(uid) not in config.languages:
				states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
				m = markup(db, states[uid]['cur'])
				text = db.get_message(states[uid]['cur'])[0]
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
				return

			if str(message.contact.user_id) == uid:
				phone = message.contact.phone_number

				db.set_phone(uid, phone)
				states[uid]['cur'] = 'main_menu'
				states[uid]['path'] = [states[uid]['cur']]
				m = markup(db, states[uid]['cur'], lang=lang)
				sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
				bot.send_sticker(uid, sticker_id, reply_markup=m)
			else:
				states[uid]['cur'] = 'send_phone_menu'
				states[uid]['path'] = [states[uid]['cur']]
				text = db.get_message("wrong_contact", lang=lang)
				m = markup(db, states[uid]['cur'], lang=lang)
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


@bot.message_handler(func=lambda m: not SQLighter().has_phone(str(m.from_user.id)),
					 content_types=['text', 'contact'])
def phone_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		lang = db.get_lang(uid)

		if not lang or not db.has_user(uid):
			log(uid, "User {} has no lang".format(uid), func_name=sys._getframe().f_code.co_name)
			states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
			m = markup(db, states[uid]['cur'])
			text = db.get_message(states[uid]['cur'])[0]
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			return

		if message.text:
			log(uid, message.text, func_name=sys._getframe().f_code.co_name)
			states[uid]['cur'] = 'send_phone_menu'
			states[uid]['path'] = [states[uid]['cur']]
			text = db.get_message("wrong_contact", lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
		else:
			if str(message.contact.user_id) == uid:
				log(uid, "phone: +" + message.contact.phone_number, func_name=sys._getframe().f_code.co_name)
				phone = message.contact.phone_number

				db.set_phone(uid, phone)
				states[uid]['cur'] = 'main_menu'
				states[uid]['path'] = [states[uid]['cur']]
				m = markup(db, states[uid]['cur'], lang=lang)
				sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
				bot.send_sticker(uid, sticker_id, reply_markup=m)
			else:
				log(uid, "Wrong contact from {0}".format(uid), func_name=sys._getframe().f_code.co_name)
				text = db.get_message('wrong_contact', lang=lang)
				bot.send_message(uid, text, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Выводит стартовое меню
@bot.message_handler(func=lambda m: utils.get_lang(str(m.from_user.id)) in config.languages
									and m.text == '/start')
@bot.message_handler(func=lambda m: m.text in SQLighter().get_buttons('main_menu_button'))
@bot.message_handler(func=lambda m: SQLighter().has_user(str(m.from_user.id))
									and SQLighter().has_phone(str(m.from_user.id))
									and str(m.from_user.id) not in Shelver().conn)
def main_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if db.is_stopped_bot(uid):
			db.user_unblocked_bot(uid)

		states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
		m = markup(db, states[uid]['cur'], lang=lang)
		sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
		bot.send_sticker(uid, sticker_id, reply_markup=m)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO обработка кнопки Назад
@bot.message_handler(func=lambda m: m.text in SQLighter().get_buttons('back_button'))
def back_handler(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if states[uid]['cur'] == 'aventos_choose_menu':
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, sticker_id, reply_markup=m)

		elif states[uid]['cur'] == 'material_choose_menu':
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			if 'aventos' in states[uid]:
				del states[uid]['aventos']
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'height_choose_menu':
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			if 'material' in states[uid]:
				del states[uid]['material']
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'width_choose_menu':
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			if 'height' in states[uid]:
				del states[uid]['height']
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'thickness_hull_choose_menu':
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message('choose_button', lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'height_facade_choose_menu':
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			if 'thickness_hull' in states[uid]:
				del states[uid]['thickness_hull']
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'width_facade_choose_menu':
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			if 'height_facade' in states[uid]:
				del states[uid]['height_facade']
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'catalog_menu':
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, sticker_id, reply_markup=m)

		elif states[uid]['cur'] == 'price_menu':
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, sticker_id, reply_markup=m)

		elif states[uid]['cur'] in db.get_products(lang):
			states[uid]['path'].pop()
			states[uid]['cur'] = states[uid]['path'][-1]
			m = markup(db, states[uid]['cur'], lang=lang)
			if states[uid]['cur'] == 'catalog_menu':
				text = db.get_message(states[uid]['cur'], lang=lang)
				pic_id = db.get_buttons('catalog_picture')
				if pic_id:
					bot.send_photo(uid, pic_id[0], caption=text, reply_markup=m, disable_notification=True)
				else:
					bot.send_message(uid, text, reply_markup=m, parse_mode='HTML', disable_notification=True)
			else:
				text = states[uid]['cur']
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif states[uid]['cur'] == 'disclamer_menu':
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, sticker_id, reply_markup=m)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO админка
@bot.message_handler(func=lambda m: SQLighter().is_admin(str(m.from_user.id)),
					 commands=['help', 'stats', 'ban', 'unban', 'post', 'change_price'])
def handle_admin_message(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if message.text == '/help':
			text = db.get_message('admin_help_message', lang=lang)
			bot.send_message(uid, text, parse_mode='HTML')

		elif message.text.split()[0] == '/ban':
			if len(message.text.split()) != 2:
				text = db.get_message('usage_ban_command', lang=lang)
				bot.send_message(uid, text, parse_mode='HTML')
				return
			else:
				ban_uid = message.text.split()[1]
				if db.has_user(ban_uid):
					db.ban_user(ban_uid)
					ban_user_lang = db.get_lang(ban_uid)
					admins = '\n'.join(config.admin_nicknames)
					ban_text = db.get_message('you_banned_message', lang=ban_user_lang).format(admins)
					try:
						bot.send_message(ban_uid, ban_text, parse_mode='HTML')
					except:
						pass
					text = db.get_message('user_banned_message', lang=lang).format(ban_uid)
					bot.send_message(uid, text, parse_mode='HTML')
				else:
					text = db.get_message('no_such_user_message', lang=lang).format(ban_uid)
					bot.send_message(uid, text, parse_mode='HTML')

		elif message.text.split()[0] == '/unban':
			if len(message.text.split()) != 2:
				text = db.get_message('usage_unban_command', lang=lang)
				bot.send_message(uid, text, parse_mode='HTML')
				return
			else:
				unban_uid = message.text.split()[1]
				if db.has_user(unban_uid):
					db.unban_user(unban_uid)
					unban_user_lang = db.get_lang(unban_uid)
					unban_text = db.get_message('you_unbanned_message', lang=unban_user_lang)
					try:
						states[unban_uid] = {'cur': 'main_menu', 'path': ['main_menu']}
						m = markup(db, states[unban_uid]['cur'], lang=unban_user_lang)
						bot.send_message(unban_uid, unban_text, reply_markup=m, parse_mode='HTML')
					except:
						pass
					text = db.get_message('user_unbanned_message', lang=lang).format(unban_uid)
					bot.send_message(uid, text, parse_mode='HTML')
				else:
					text = db.get_message('no_such_user_message', lang=lang).format(unban_uid)
					bot.send_message(uid, text, parse_mode='HTML')

		elif message.text == '/stats':
			active_users_count = db.get_active_users_count()
			blocked_bot_users_count = db.get_stopped_bot_users_count()
			banned_users_count = db.get_banned_users_count()
			total = db.get_total_users_count()

			text = db.get_message('stats_message', lang=lang).format(active_users_count,
																	 blocked_bot_users_count,
																	 banned_users_count,
																	 total)
			bot.send_message(uid, text, parse_mode='HTML')
			# TODO потестить
			if os.path.exists(config.users_excel_filename):
				excel.save_users_to_file(config.users_excel_filename)
			else:
				file = open(config.users_excel_filename, "wb")
				file.close()
				excel.save_users_to_file(config.users_excel_filename)

			with open(config.users_excel_filename, "rb") as file:
				bot.send_document(uid, file)

		elif message.text == '/post':
			states[uid] = {'cur': 'post_menu', 'path': ['post_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif message.text == '/change_price':
			states[uid] = {'cur': 'change_price_menu', 'path': ['change_price_menu']}
			m = markup(db, states[uid]['cur'], lang='ru')
			text = db.get_message('select_price_list', lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# TODO Обработка файлов
@bot.message_handler(func=lambda m: SQLighter().is_admin(str(m.from_user.id))
									and Shelver().conn[str(m.from_user.id)]['cur'] == 'post_menu',
					 content_types=['document', 'photo', 'video', 'audio', 'sticker', 'location', 'text'])
def media_post_handler(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if message.text and message.text == db.get_buttons('post_button', lang=lang)[0]:
			if 'post' in states[uid]:
				post(states[uid]['post'], [uid])
				states[uid]['cur'] = 'make_post?'
				states[uid]['path'] = ['make_post?']
				text = db.get_message('make_post?', lang=lang)
				m = markup(db, 'make_post?', lang=lang)
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			else:
				text = db.get_message('post_is_empty', lang=lang)
				bot.send_message(uid, text, parse_mode='HTML')

		elif message.text and message.text == db.get_buttons('show_post_button', lang=lang)[0]:
			if 'post' in states[uid]:
				post(states[uid]['post'], [uid])
			else:
				text = db.get_message('post_is_empty', lang=lang)
				bot.send_message(uid, text, parse_mode='HTML')

		else:
			if 'post' not in states[uid]:
				states[uid]['post'] = [message]
			else:
				states[uid]['post'].append(message)


@bot.message_handler(func=lambda m: SQLighter().is_admin(str(m.from_user.id))
									and Shelver().conn[str(m.from_user.id)]['cur'] == 'make_post?')
def make_post(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if message.text == db.get_buttons('post_button', lang=lang)[0]:
			user_ids = db.get_user_ids()
			pub_thread = Thread(target=post, args=(states[uid]['post'], user_ids))
			pub_thread.start()
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			text = db.get_message(states[uid]['cur'], lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			return

		if message.text == db.get_buttons('change_post_button', lang=lang)[0]:
			states[uid] = {'cur': 'post_menu', 'path': ['post_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			return


# TODO Выбор прайса для изменения
@bot.message_handler(func=lambda m: SQLighter().is_admin(str(m.from_user.id))
									and Shelver().conn[str(m.from_user.id)]['cur'] == 'change_price_menu')
def change_price_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		categories = db.get_buttons('catalog_menu', lang='ru') + db.get_buttons('full_price_button', lang='ru')
		if message.text in categories:
			states[uid]['new_price_category'] = message.text
			text = db.get_message('send_new_price', lang=lang)
			m = markup(db, 'remove')
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# TODO Обработка и обновление ссылки прайс-листа
@bot.message_handler(func=lambda m: SQLighter().is_admin(str(m.from_user.id))
									and Shelver().conn[str(m.from_user.id)]['cur'] == 'change_price_menu'
									and 'new_price_category' in Shelver().conn[str(m.from_user.id)],
					 content_types=['document'])
def document_handler(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, "New price list: " + message.document.file_id, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		new_price_file_id = message.document.file_id
		db.update_price_list(states[uid]['new_price_category'], new_price_file_id)
		text = db.get_message('price_updated', lang=lang).format(states[uid]['new_price_category'])
		states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
		m = markup(db, states[uid]['cur'], lang=lang)
		bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# @bot.message_handler(commands=['help'])
# def help_handler(message):
# 	with SQLighter() as db, Shelver().conn as states:
# 		uid = str(message.from_user.id)
# 		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
# 		lang = db.get_lang(uid)
#
# 		if message.text == '/help':
# 			text = db.get_message('user_help_message', lang=lang)
# 			bot.send_message(uid, text, parse_mode='HTML')

# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка кнопок главного меню
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'main_menu')
def handle_main_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if message.text == db.get_buttons('calculator_button', lang=lang)[0]:
			if db.is_continued(uid):
				states[uid]['cur'] = 'aventos_choose_menu'
				if states[uid]['cur'] not in states[uid]['path']:
					states[uid]['path'].append(states[uid]['cur'])

				m = markup(db, states[uid]['cur'], lang=lang)
				text = db.get_message(states[uid]['cur'], lang=lang)
				pic_id = db.get_buttons('aventos_picture')[0]
				try:
					bot.send_photo(uid, pic_id, caption=text, reply_markup=m, disable_notification=True)
				except Exception as e:
					print(e)
					bot.send_message(uid, text, reply_markup=m, parse_mode='HTML', disable_notification=True)
			else:
				states[uid]['cur'] = 'disclamer_menu'
				if states[uid]['cur'] not in states[uid]['path']:
					states[uid]['path'].append(states[uid]['cur'])

				m = markup(db, states[uid]['cur'], lang=lang)
				text = db.get_message(states[uid]['cur'], lang=lang)
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML', disable_notification=True)

		elif message.text == db.get_buttons('catalog_button', lang=lang)[0]:
			states[uid]['cur'] = 'catalog_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])
			text = db.get_message(states[uid]['cur'], lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			pic_id = db.get_buttons('catalog_picture')
			if pic_id:
				bot.send_photo(uid, pic_id[0], caption=text, reply_markup=m, disable_notification=True)
			else:
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML', disable_notification=True)

		elif message.text == db.get_buttons('price_button', lang=lang)[0]:
			states[uid]['cur'] = 'price_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])
			text = db.get_message(states[uid]['cur'], lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML', disable_notification=True)

		elif message.text == db.get_buttons('change_lang_button', lang=lang)[0]:
			states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
			m = markup(db, 'lang_menu')
			text = db.get_message('lang_menu')
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif message.text == db.get_buttons('contacts_button', lang=lang)[0]:
			msgs = db.get_message('contacts', many_messages=True, lang=lang)
			for msg in msgs:
				bot.send_message(uid, msg, parse_mode='HTML', disable_notification=True)
		else:
			states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
			m = markup(db, states[uid]['cur'], lang=lang)
			sticker_id = db.get_message(states[uid]['cur'] + "_sticker", lang=lang)
			bot.send_sticker(uid, sticker_id, reply_markup=m)


# elif message.text == db.get_buttons('change_phone_button', lang=lang)[0]:
# 	states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 	m = markup(db, states[uid]['cur'], lang=lang)
# 	text = db.get_message(states[uid]['cur'], lang=lang)
# 	bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка кнопок прайс меню
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'price_menu')
def handle_price_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if message.text in db.get_buttons('full_price_list', lang=lang) + db.get_buttons('catalog_menu', lang=lang):
			text = message.text
			file_id = db.get_price(text, lang)
			try:
				bot.send_document(uid, file_id, disable_notification=True)
			except:
				print("Can't send instruction " + text)
				bot.send_message(uid, text, parse_mode='HTML', disable_notification=True)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка каталога
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'catalog_menu'
									and utils.is_in_catalog(m.text, SQLighter().get_lang(str(m.from_user.id))))
@bot.message_handler(
	func=lambda m: utils.is_in_catalog(state(str(m.from_user.id)), SQLighter().get_lang(str(m.from_user.id)))
				   and SQLighter().is_in_submenu(
		state(str(m.from_user.id)),
		m.text,
		SQLighter().get_lang(str(m.from_user.id))))
def handle_first_catalog_menu(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if (db.has_instruction(message.text, lang=lang) and message.text in db.finaly_dirs()) \
				or (message.text not in db.finaly_dirs()):

			states[uid]['cur'] = message.text
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])
			caption = db.get_caption(message.text, lang)
			photos = db.get_photos(message.text, lang)
			videos = db.get_videos(message.text, lang)

			m = markup(db, states[uid]['cur'], lang=lang)

			if photos + videos == []:
				if caption:
					bot.send_message(uid, caption, parse_mode='HTML', reply_markup=m, disable_notification=True)
				else:
					bot.send_message(uid, states[uid]['cur'], parse_mode='HTML', reply_markup=m,
									 disable_notification=True)
			else:
				if not videos:
					for photo in photos[:-1]:
						try:
							bot.send_photo(uid, photo, disable_notification=True)
						except:
							bot.send_message(uid, 'picture')
					try:
						bot.send_photo(uid, photos[-1], caption=caption, reply_markup=m, disable_notification=True)
					except:
						bot.send_message(uid, caption, reply_markup=m)
				else:
					for photo in photos:
						try:
							bot.send_photo(uid, photo, disable_notification=True)
						except:
							bot.send_message(uid, 'picture')
					for video in videos[:-1]:
						# send as document потому что gif
						try:
							bot.send_document(uid, video, disable_notification=True)
						except:
							bot.send_message(uid, 'video')
					try:
						bot.send_document(uid, videos[-1], caption=caption, reply_markup=m, disable_notification=True)
					except:
						bot.send_message(uid, caption, reply_markup=m)
		else:
			caption = db.get_caption(message.text, lang)
			photos = db.get_photos(message.text, lang)
			videos = db.get_videos(message.text, lang)

			if photos + videos == []:
				if caption:
					bot.send_message(uid, caption, parse_mode='HTML', disable_notification=True)
				else:
					bot.send_message(uid, states[uid]['cur'], parse_mode='HTML', disable_notification=True)
			else:
				if not videos:
					for photo in photos[:-1]:
						try:
							bot.send_photo(uid, photo, disable_notification=True)
						except:
							bot.send_message(uid, 'picture')
					try:
						bot.send_photo(uid, photos[-1], caption=caption, disable_notification=True)
					except:
						bot.send_message(uid, caption)
				else:
					for photo in photos:
						try:
							bot.send_photo(uid, photo, disable_notification=True)
						except:
							bot.send_message(uid, 'picture')
					for video in videos[:-1]:
						# send as document потому что gif
						try:
							bot.send_document(uid, video, disable_notification=True)
						except:
							bot.send_message(uid, 'video')
					try:
						bot.send_document(uid, videos[-1], caption=caption, disable_notification=True)
					except:
						bot.send_message(uid, caption)


# *****************************************************************************************************
# *****************************************************************************************************

def full_instruction_filter_1(m):
	user_id = str(m.from_user.id)
	with SQLighter() as db, Shelver().conn as states:
		if not states.get(user_id) or 'aventos' not in states.get(user_id):
			return False
		user_lang = db.get_lang(user_id)
		s = state(user_id)
		buttons = db.get_buttons('full_instruction_button', lang=user_lang)
		has_instr = db.has_instruction(states[user_id]['aventos'], lang=user_lang)
		return s == 'recomendation_menu' and m.text in buttons and has_instr


def full_instruction_filter_2(m):
	user_id = str(m.from_user.id)
	with SQLighter() as db, Shelver().conn as states:
		if not states.get(user_id) or 'cur' not in states.get(user_id):
			return False
		user_lang = db.get_lang(user_id)
		has_instr = db.has_instruction(states[user_id]['cur'], lang=user_lang)
		buttons = db.get_buttons('instruction_button', lang=user_lang)
	return m.text in buttons and state(user_id) != 'aventos_choose_menu' and has_instr


# TODO Обработка кнопки Полная инструкция
@bot.message_handler(func=full_instruction_filter_1)
@bot.message_handler(func=full_instruction_filter_2)
def handle_full_instruction(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if states[uid]['cur'] == 'recomendation_menu':
			aventos = states[uid]['aventos']
		else:
			aventos = states[uid]['cur']
		text = db.get_instruction_message(aventos, lang)

		videos = db.get_instruction_videos(aventos, lang)
		photos = db.get_instruction_photos(aventos, lang)
		documents = db.get_instruction_documents(aventos, lang)

		if text is not None and text != '':
			bot.send_message(uid, text, parse_mode='HTML', disable_notification=True)

		for video in videos:
			try:
				bot.send_video(uid, video, disable_notification=True)
			except:
				# trying send as document
				try:
					bot.send_document(uid, video, disable_notification=True)
				except Exception as e:
					print(e)

		for photo in photos:
			try:
				bot.send_photo(uid, photo, disable_notification=True)
			except Exception as e:
				print(e)

		for doc in documents:
			try:
				bot.send_document(uid, doc, disable_notification=True)
			except Exception as e:
				print(e)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO обработка кнопки Регулировка Aventos
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == "recomendation_menu"
									and m.text in SQLighter().get_buttons("aventos_setting_menu",
																		  lang=SQLighter().get_lang(
																			  str(m.from_user.id))))
def handle_setting_button(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		video = db.get_buttons('aventos_setting_' + states[uid]['aventos'])[0]
		try:
			bot.send_video(uid, video, disable_notification=True)
		except:
			try:
				bot.send_document(uid, video, disable_notification=True)
			except Exception as e:
				print(e)


# *****************************************************************************************************
# *****************************************************************************************************

@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'disclamer_menu'
									and m.text == SQLighter().get_buttons('continue_button',
																		  lang=SQLighter().get_lang(
																			  str(m.from_user.id)))[0])
def handle_continue_button(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		db.user_continued(uid)
		states[uid]['cur'] = 'aventos_choose_menu'
		states[uid]['path'].pop(states[uid]['path'].index('disclamer_menu'))
		if states[uid]['cur'] not in states[uid]['path']:
			states[uid]['path'].append(states[uid]['cur'])

		m = markup(db, states[uid]['cur'], lang=lang)
		text = db.get_message(states[uid]['cur'], lang=lang)
		pic_id = db.get_buttons('aventos_picture')[0]
		try:
			bot.send_photo(uid, pic_id, caption=text, reply_markup=m, disable_notification=True)
		except Exception as e:
			print(e)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML', disable_notification=True)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка выбора авентоса
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'aventos_choose_menu')
def handle_aventos_choose(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		# if message.text in db.get_buttons('aventos_choose_menu', lang=lang):
		if message.text in db.get_mechanism_types():
			states[uid]['aventos'] = message.text
			states[uid]['cur'] = 'material_choose_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка выбора материала и толщины
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'material_choose_menu')
def handle_material_choose(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if message.text in db.get_buttons('material_choose_menu', lang=lang):
			states[uid]['material'] = message.text
			states[uid]['cur'] = 'height_choose_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO обработка ввода высоты корпуса
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'height_choose_menu')
def handle_height_choose(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)

		if not message.text.isdigit():
			text = db.get_message('input_only_number_message', lang=lang)
			bot.send_message(uid, text, parse_mode='HTML')
			return

		if 'aventos' not in states[uid]:
			log(uid, "'aventos' not in states[{}]".format(uid), func_name=sys._getframe().f_code.co_name)
			send_error_and_change_state(bot, states, uid, db)
			return

		if states[uid]['aventos'] in config.height_boundaries \
				and not (config.height_boundaries[states[uid]['aventos']]['min'] <= int(message.text) <=
						 config.height_boundaries[states[uid]['aventos']]['max']):
			_min = config.height_boundaries[states[uid]['aventos']]['min']
			_max = config.height_boundaries[states[uid]['aventos']]['max']
			text = db.get_message('wrong_value', lang=lang).format(_min, _max)
			bot.send_message(uid, text, parse_mode='HTML')

		else:
			states[uid]['height'] = int(message.text)
			states[uid]['cur'] = 'width_choose_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка ввода ширины корпуса
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'width_choose_menu')
def handle_height_choose(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if not message.text.isdigit():
			text = db.get_message('input_only_number_message', lang=lang)
			bot.send_message(uid, text, parse_mode='HTML')

		if 'aventos' not in states[uid]:
			log(uid, "'aventos' not in states[{}]".format(uid), func_name=sys._getframe().f_code.co_name)
			send_error_and_change_state(bot, states, uid, db)
			return

		if states[uid]['aventos'] in config.width_boundaries \
				and not (config.width_boundaries[states[uid]['aventos']]['min'] <= int(message.text) <=
						 config.width_boundaries[states[uid]['aventos']]['max']):
			_min = config.width_boundaries[states[uid]['aventos']]['min']
			_max = config.width_boundaries[states[uid]['aventos']]['max']
			text = db.get_message('wrong_value', lang=lang).format(_min, _max)
			bot.send_message(uid, text, parse_mode='HTML')
		else:
			states[uid]['width'] = int(message.text)
			thickness = int(states[uid]['material'].split(" ")[1])
			weight = states[uid]['height'] / 1000 * states[uid]['width'] / 1000 * thickness / 1000 * config.density[
				states[uid]['material']]
			coef = states[uid]['height'] * weight

			states[uid]['cur'] = 'recomendation_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			if states[uid]['aventos'] not in config.mechanism_with_height_parameter:
				recomendation_mechanism = utils.get_recomendation_mechanism(coef, states[uid]['aventos'])
			else:
				if states[uid]['aventos'] == 'AVENTOS HS':
					states[uid]['height'] = utils.round_height(states[uid]['height'])
				recomendation_mechanism = utils.get_recomendation_mechanism(weight, states[uid]['aventos'],
																			height=states[uid]['height'])
			recomendation_lever = db.get_recomendation_lever(states[uid]['height'], states[uid]['aventos'])

			if len(recomendation_mechanism) == 0:
				if states[uid]['aventos'] in ('AVENTOS HK-XS', 'AVENTOS HK-XS TIP-ON'):
					mechanism_text = db.get_message('need_additional_mechanism', lang=lang)
				else:
					mechanism_text = db.get_message('no_mechanism', lang=lang)
			else:
				mechanism_text = (" " + db.get_message('or', lang=lang) + " ").join(recomendation_mechanism)

			if len(recomendation_lever) == 0 and states[uid]['aventos'] in config.mechanism_with_lever:
				lever_text = db.get_message('no_lever', lang=lang)
			else:
				lever_text = (" " + db.get_message('or', lang=lang) + " ").join(recomendation_lever)

			if states[uid]['aventos'] in config.mechanism_with_lever:
				text = db.get_message(states[uid]['cur'], lang=lang).format(
					str(states[uid]['material']),
					str(int(states[uid]['height'])),
					str(int(states[uid]['width'])),
					str(int(coef)),
					mechanism_text,
					lever_text,
					states[uid]['aventos'],
					weight * 1.0
				)
			else:
				text = db.get_message("recomendation_menu_without_lever", lang=lang).format(
					str(states[uid]['material']),
					str(int(states[uid]['height'])),
					str(int(states[uid]['width'])),
					str(int(coef)),
					mechanism_text,
					states[uid]['aventos'],
					weight * 1.0
				)

			if len(recomendation_mechanism) == 0:
				states[uid]['cur'] = 'material_choose_menu'
				states[uid]['path'].pop()
				states[uid]['path'].pop()
				if 'width' in states[uid]:
					del states[uid]['width']
				if 'height' in states[uid]:
					del states[uid]['height']
				text += "\n\n" + db.get_message('change_parameters', lang=lang)

			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
			if len(recomendation_mechanism) != 0:
				pic_id = db.get_buttons('recomendation_picture_' + states[uid]['aventos'])[0]
				if states[uid]['aventos'] == 'AVENTOS HF':
					text = db.get_message('position_with_h', lang=lang).format(
						utils.compute_height(states[uid]['aventos'], states[uid]['height']))
				elif states[uid]['aventos'] in ('AVENTOS HK-XS', 'AVENTOS HK-XS TIP-ON'):
					text = db.get_message('position_for_hk_xs', lang=lang)
				else:
					text = db.get_message('position_without_h', lang=lang)

				try:
					bot.send_photo(uid, pic_id, caption=text)
				except Exception as e:
					bot.send_message(uid, text)
					print("Exception while sending photo: ", e)


# *****************************************************************************************************
# *****************************************************************************************************

# TODO После рекомендации
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'recomendation_menu')
def asd(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if message.text in db.get_buttons('change_parameters'):
			states[uid]['cur'] = 'material_choose_menu'
			states[uid]['path'].pop()
			states[uid]['path'].pop()
			states[uid]['path'].pop()
			if 'width' in states[uid]:
				del states[uid]['width']
			if 'height' in states[uid]:
				del states[uid]['height']
			text = db.get_message('change_parameters', lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')

		elif message.text in db.get_buttons('ustanovka_otvetnoy_planki'):
			states[uid]['cur'] = 'thickness_hull_choose_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])
			text = db.get_message(states[uid]['cur'], lang=lang)
			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка толщины фасада
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'thickness_hull_choose_menu')
def asd(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if message.text not in ('16', '18'):
			text = db.get_message('choose_menu_button', lang=lang)
			bot.send_message(uid, text, parse_mode='HTML')

		else:
			states[uid]['thickness_hull'] = int(message.text)
			states[uid]['cur'] = 'height_facade_choose_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			m = markup(db, states[uid]['cur'], lang=lang)
			if states[uid]['aventos'] == 'AVENTOS HF':
				text = db.get_message(states[uid]['cur'] + "_down", lang=lang)
			else:
				text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка высоты фасада
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'height_facade_choose_menu')
def asd(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if not message.text.isdigit():
			text = db.get_message('input_only_number_message', lang=lang)
			bot.send_message(uid, text, parse_mode='HTML')

		else:
			states[uid]['height_facade'] = int(message.text)
			states[uid]['cur'] = 'width_facade_choose_menu'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			m = markup(db, states[uid]['cur'], lang=lang)
			text = db.get_message(states[uid]['cur'], lang=lang)
			bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')


# *****************************************************************************************************
# *****************************************************************************************************

# TODO Обработка ширины фасада
@bot.message_handler(func=lambda m: state(str(m.from_user.id)) == 'width_facade_choose_menu')
def asd(message):
	with SQLighter() as db, Shelver().conn as states:
		uid = str(message.from_user.id)
		log(uid, message.text, func_name=sys._getframe().f_code.co_name)
		lang = db.get_lang(uid)
		if not message.text.isdigit():
			text = db.get_message('input_only_number_message', lang=lang)
			bot.send_message(uid, text, parse_mode='HTML')

		else:
			states[uid]['width_facade'] = int(message.text)
			states[uid]['cur'] = 'ustanovka_planki_recommendation'
			if states[uid]['cur'] not in states[uid]['path']:
				states[uid]['path'].append(states[uid]['cur'])

			a = int(states[uid]['material'].split(" ")[1])
			b = states[uid]['height']
			c = states[uid]['width']
			d = states[uid]['thickness_hull']
			e = states[uid]['height_facade']
			f = states[uid]['width_facade']
			lever_value = None
			if states[uid]['aventos'] == 'AVENTOS HL':
				recommendation_lever = db.get_recomendation_lever(states[uid]['height'], states[uid]['aventos'])
				if not recommendation_lever:
					raise Exception("Need HL lever for x, y parameters")
				lever_value = [config.hl_lever_values_for_x_y[lever] for lever in recommendation_lever]

			x, y = utils.compute_x_y(states[uid]['aventos'], a, b, c, d, e, f, lever_value=lever_value)
			pic_id = db.get_buttons('counterplate_picture_' + states[uid]['aventos'])[0]

			if states[uid]['aventos'] == 'AVENTOS HF':
				msg = db.get_message('your_data_conterplate_' + states[uid]['aventos'], lang=lang).format(
					states[uid]['thickness_hull'],
					states[uid]['height_facade'],
					states[uid]['width_facade']
				)
			else:
				msg = db.get_message('your_data_conterplate', lang=lang).format(
					states[uid]['thickness_hull'],
					states[uid]['height_facade'],
					states[uid]['width_facade']
				)

			if 'thickness_hull' in states[uid]:
				del states[uid]['thickness_hull']
			if 'height_facade' in states[uid]:
				del states[uid]['height_facade']
			if 'width_facade' in states[uid]:
				del states[uid]['width_facade']
			if states[uid]['aventos'] not in ('AVENTOS HK-XS', 'AVENTOS HK-XS TIP-ON', 'AVENTOS HL'):
				text = db.get_message(states[uid]['cur'], lang=lang).format(x, y)
			elif states[uid]['aventos'] == 'AVENTOS HL':
				text = db.get_message(states[uid]['cur'] + "_AVENTOS HL", lang=lang)
				if_lever_text = db.get_message('if_lever', lang=lang)
				for index, i in enumerate(x):
					text += "\nX = {0}, ".format(i) + if_lever_text + " " + recommendation_lever[index]
				text += "\nY = {0}".format(y[0])
			else:
				text = db.get_message(states[uid]['cur'] + "_exception", lang=lang).format(x[0], x[1], x[2], y)

			states[uid]['cur'] = 'recomendation_menu'
			states[uid]['path'] = states[uid]['path'][0:states[uid]['path'].index('recomendation_menu') + 1]

			m = markup(db, states[uid]['cur'], lang=lang)
			bot.send_message(uid, msg, parse_mode='HTML', disable_notification=True)
			try:
				bot.send_photo(uid, pic_id, caption=text, reply_markup=m)
			except Exception as e:
				bot.send_message(uid, text, reply_markup=m, parse_mode='HTML')
				print("Exception while sending photo: ", e)


# *****************************************************************************************************
# *****************************************************************************************************


if __name__ == "__main__":
	bot.remove_webhook()
	bot.polling(none_stop=True)
