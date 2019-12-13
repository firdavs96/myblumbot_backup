# -*-coding: utf-8 -*-

from bot.sqlighter import SQLighter
from telebot import types
import bot.config as config


def markup(db, cur_step, *, lang=None):
	if cur_step in ('banned_markup', 'remove'):
		m = types.ReplyKeyboardRemove()
		return m
	
	m = types.ReplyKeyboardMarkup(resize_keyboard=True)
	
	if cur_step == 'post_menu':
		post_btn = db.get_buttons('post_button', lang=lang)[0]
		m.add(post_btn)
		show_btn = db.get_buttons('show_post_button', lang=lang)[0]
		m.add(show_btn)
		main_btn = db.get_buttons('main_menu_button', lang=lang)[0]
		m.add(main_btn)
		return m
	
	elif cur_step == 'make_post?':
		post_btn = db.get_buttons('post_button', lang=lang)[0]
		m.add(post_btn)
		chng_btn = db.get_buttons('change_post_button', lang=lang)[0]
		m.add(chng_btn)
		main_btn = db.get_buttons('main_menu_button', lang=lang)[0]
		m.add(main_btn)
	
	elif cur_step == 'lang_menu':
		btns = db.get_buttons(cur_step)
		m.add(btns[0], btns[1])
	
	elif cur_step == 'send_phone_menu':
		m = types.ReplyKeyboardMarkup()
		btns = db.get_buttons(cur_step, lang=lang)
		contact = types.KeyboardButton(btns[0], request_contact=True)
		m.add(contact)
	
	elif cur_step == 'main_menu':
		btns = db.get_buttons(cur_step, lang=lang)
		# if len(btns) % 2 == 0:
		# 	for i in range(0, len(btns), 2):
		# 		m.add(btns[i], btns[i + 1])
		# else:
		# 	for i in range(0, len(btns) - 1, 2):
		# 		m.add(btns[i], btns[i + 1])
		# 	m.add(btns[-1])
		#['\U0001f6e0 Подбор + Установка Aventos', '📦 Продукция', '☎️ Контакты', '📝 Прайс-лист', '🔄 Сменить язык']
		m.add(btns[0])
		m.add(btns[1], btns[3])
		m.add(btns[2], btns[4])
			
	elif cur_step == 'price_menu':
		full_price = db.get_buttons('full_price_button', lang=lang)[0]
		m.add(full_price)
		btns = db.get_buttons('catalog_menu', lang=lang)
		for i in btns:
			m.add(i)
		back_btn = db.get_buttons('back_button', lang=lang)[0]
		m.add(back_btn)
	
	elif cur_step == 'change_price_menu':
		full_price = db.get_buttons('full_price_button', lang=lang)[0]
		m.add(full_price)
		btns = db.get_buttons('catalog_menu', lang=lang)
		for i in btns:
			m.add(i)
		main_btn = db.get_buttons('main_menu_button', lang=lang)[0]
		m.add(main_btn)
		
	elif cur_step == 'catalog_menu':
		btns = db.get_buttons(cur_step, lang=lang)
		for i in btns:
			m.add(i)
		back_btn = db.get_buttons('back_button', lang=lang)[0]
		m.add(back_btn)
		
	elif cur_step in db.get_products(lang):
		if cur_step not in db.finaly_dirs():
			btns = db.get_submenu(cur_step, lang)
			for i in btns:
				m.add(i)
			back_btn = db.get_buttons('back_button', lang=lang)[0]
			m.add(back_btn)
		else:
			a = db.get_buttons('instruction_button', lang=lang)[0]
			m.add(a)
			back_btn = db.get_buttons('back_button', lang=lang)[0]
			m.add(back_btn)
			main_btn = db.get_buttons('main_menu_button', lang=lang)[0]
			m.add(main_btn)
			
				
	elif cur_step == 'disclamer_menu':
		btns = db.get_buttons(cur_step, lang=lang)
		m.add(btns[0])
		back_btn = db.get_buttons('back_button', lang=lang)[0]
		m.add(back_btn)
			
	elif cur_step == 'aventos_choose_menu':
		btns = db.get_mechanism_types()
		
		if len(btns) % 2 == 0:
			for i in range(0, len(btns), 2):
				m.add(btns[i], btns[i + 1])
		else:
			for i in range(0, len(btns) - 1, 2):
				m.add(btns[i], btns[i + 1])
			m.add(btns[-1])
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	elif cur_step == 'material_choose_menu':
		btns = db.get_buttons(cur_step, lang=lang)
		for i in range(0, len(btns), 2):
			m.add(btns[i], btns[i + 1])
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	elif cur_step == 'height_choose_menu':
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	elif cur_step == 'width_choose_menu':
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	elif cur_step == 'recomendation_menu':
		btns = db.get_buttons(cur_step, lang=lang)
		main_btn = db.get_buttons('main_menu_button', lang=lang)[0]
		for index, btn in enumerate(btns):
			if index == len(btns) - 1:
				m.add(main_btn, btn)
			else:
				m.add(btn)
	
	elif cur_step == 'thickness_hull_choose_menu':
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add('16', '18')
		m.add(back_btn[0])
	
	elif cur_step == 'height_facade_choose_menu':
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	elif cur_step == 'width_facade_choose_menu':
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	elif cur_step == 'ustanovka_planki_recommendation':
		back_btn = db.get_buttons('back_button', lang=lang)
		m.add(back_btn[0])
	
	return m
