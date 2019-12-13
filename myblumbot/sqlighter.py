# -*- coding: utf-8 -*-
import sqlite3
import time
from datetime import datetime
import myblumbot.config as config


class SQLighter:
	def __init__(self, database=config.database_name):
		self.connection = sqlite3.connect(database)
		self.cursor = self.connection.cursor()

	def close(self):
		""" Закрываем текущее соединение с БД """
		self.connection.close()

	def __enter__(self):
		return self

	def __exit__(self, Type, Value, Trace):
		self.close()

	def get_buttons(self, step, *, lang=None):
		with self.connection:
			if lang is None:
				q = "SELECT text FROM button WHERE step = ? AND deleted = 0"
				result = self.cursor.execute(q, (step,)).fetchall()
			else:
				q = "SELECT text FROM button WHERE step = ? AND lang = ? AND deleted = 0"
				result = self.cursor.execute(q, (step, lang)).fetchall()
			return [i[0] for i in result]

	def get_message(self, step, *, many_messages=False, lang=None):
		with self.connection:
			if lang is None:
				# Если язык не указан, то возвращается список сообщений
				q = "SELECT text FROM message WHERE step = ? AND deleted = 0"
				result = self.cursor.execute(q, (step,)).fetchall()
				result = [i[0] for i in result]
			else:
				# Иначе возвращаем одно сообщение, если many_messages=False
				q = "SELECT text FROM message WHERE step = ? AND lang = ? AND deleted = 0"
				result = self.cursor.execute(q, (step, lang)).fetchall()
				if many_messages:
					result = [i[0] for i in result]
				else:
					result = result[0][0] if result else None
			return result

	def has_user(self, uid):
		with self.connection:
			q = "SELECT uid FROM user WHERE uid = ?"
			res = self.cursor.execute(q, (uid,)).fetchall()
			if len(res) > 0:
				return True
			else:
				return False

	def save_user_info(self, uid, full_name, user_name, *, phone=None, lang=None):
		if config.TEST_CONFIG:
			print("User info saved: uid={uid}, fname={full_name}, uname={user_name}, phone={phone}, lang={lang}".format(
				uid=uid, full_name=full_name, user_name=user_name, phone=str(phone), lang=str(lang)))
		phone = '' if phone is None else phone
		lang = '' if lang is None else lang

		with self.connection:
			is_admin = 0
			is_banned = 0
			stopped_bot = 0
			cur_date = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
			q = "INSERT INTO user VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)"
			self.cursor.execute(q, (
				uid, full_name, user_name, phone, lang, is_admin, is_banned, stopped_bot, cur_date))

	def get_lang(self, uid):
		with self.connection:
			q = "SELECT language FROM user WHERE uid = ?"
			res = self.cursor.execute(q, (uid,)).fetchall()
			ret_value = res[0][0] if res else None
			return ret_value

	def set_lang(self, uid, lang):
		with self.connection:
			q = "UPDATE user SET language = ? WHERE uid = ?"
			self.cursor.execute(q, (lang, uid))

	def get_phone(self, uid):
		with self.connection:
			q = "SELECT phone FROM user WHERE uid = ?"
			res = self.cursor.execute(q, (uid,)).fetchone()
			return res[0] if res else res

	def set_phone(self, uid, phone):
		with self.connection:
			q = "UPDATE user SET phone = ? WHERE uid = ?"
			self.cursor.execute(q, (phone, uid))

	def has_phone(self, uid):
		with self.connection:
			q = "SELECT phone FROM user WHERE uid = ?"
			res = self.cursor.execute(q, (uid,)).fetchall()
			res = [i[0] for i in res if i[0] is not None and i[0] != '']
			return True if res else False

	def get_recomendation_mechanism_hs_hl(self, height, coef, aventos):
		with self.connection:
			q = """ SELECT DISTINCT mechanism_list.mechanism
					FROM mechanism_hs_hl
					INNER JOIN mechanism_list ON mechanism_hs_hl.mechanism_id = mechanism_list.id,
					mechanism_type_list ON mechanism_hs_hl.mechanism_type_id = mechanism_type_list.id
					WHERE mechanism_hs_hl.deleted = 0
					AND mechanism_hs_hl.height_max >= ?
					AND mechanism_hs_hl.height_min <= ?
					AND mechanism_hs_hl.weight_max >= ?
					AND mechanism_hs_hl.weight_min <= ?
					AND mechanism_type_list.mechanism_type = ?"""
			res = self.cursor.execute(q, (height, height, coef, coef, aventos)).fetchall()
			res = [i[0] for i in res if i[0] != '']
			return res

	def get_recomendation_mechanism(self, coef, aventos):
		with self.connection:
			q = """ SELECT DISTINCT mechanism_list.mechanism
					FROM mechanism
					INNER JOIN mechanism_list ON mechanism.mechanism_id = mechanism_list.id,
					mechanism_type_list ON mechanism_type_list.id = mechanism.mechanism_type_id
					WHERE mechanism.min_coef <= ?
					AND mechanism.max_coef >= ?
					AND mechanism.deleted = 0
					AND mechanism_type_list.mechanism_type = ?"""
			res = self.cursor.execute(q, (coef, coef, aventos)).fetchall()
			res = [i[0] for i in res if i[0] != '']
			return res

	def get_recomendation_lever(self, height, aventos):
		with self.connection:
			q = """ SELECT DISTINCT lever.name
					FROM lever
					INNER JOIN mechanism_type_list ON lever.mechanism_type_id = mechanism_type_list.id
					WHERE lever.min <= ?
					AND lever.max >= ?
					AND mechanism_type_list.mechanism_type = ?
					AND lever.deleted = 0"""
			res = self.cursor.execute(q, (height, height, aventos)).fetchall()
			res = [i[0] for i in res if i[0] != '']
			return res

	def get_mechanism_types(self):
		with self.connection:
			q = "SELECT mechanism_type FROM mechanism_type_list"
			res = self.cursor.execute(q).fetchall()
			res = [i[0] for i in res if i[0] != '']
			return res

	def get_final_catalog_directories(self):
		with self.connection:
			q = "SELECT name FROM catalog WHERE final_directory = 1 and deleted = 0"
			res = self.cursor.execute(q).fetchall()
			res = [i[0] for i in res if i[0] != '']
			return res

	def get_products(self, lang):
		with self.connection:
			try:
				q = "SELECT dir_name_{0} FROM catalog WHERE deleted = 0".format(lang)
				res = self.cursor.execute(q).fetchall()
				res = [j for i in res for j in i]
				return res
			except sqlite3.OperationalError:
				return []

	def get_caption(self, product, lang):
		with self.connection:
			q = """ SELECT caption_text_{0} FROM catalog_caption
					INNER JOIN catalog
					ON catalog.id = catalog_caption.step_id
					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (product,)).fetchall()
			return None if not res else res[0][0]

	def get_photos(self, product, lang):
		with self.connection:
			q = """ SELECT photo_link FROM catalog_photo
  					INNER JOIN catalog
  					ON catalog.id = catalog_photo.step_id
  					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (product,)).fetchall()
			res = [i[0] for i in res]
			return res

	def get_videos(self, product, lang):
		with self.connection:
			q = """ SELECT video_link FROM catalog_video
		  					INNER JOIN catalog
		  					ON catalog.id = catalog_video.step_id
		  					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (product,)).fetchall()
			res = [i[0] for i in res]
			return res

	def is_in_submenu(self, menu_product, submenu_product, lang):
		with self.connection:
			q = """ SELECT COUNT(*) FROM catalog,
									(SELECT * FROM catalog, catalog_hierarchy
									 WHERE catalog_hierarchy.menu_dir_id = catalog.id
									 AND catalog.dir_name_{0} = ?
									 AND deleted = 0) as new_table
					WHERE catalog.id = new_table.submenu_dir_id
					AND catalog.dir_name_{0} = ?
					AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (menu_product, submenu_product)).fetchall()[0][0]
			return True if res else False

	def finaly_dirs(self):
		with self.connection:
			q = """ SELECT dir_name_ru, dir_name_uz FROM catalog WHERE deleted = 0 AND is_final_dir = 1"""
			res = self.cursor.execute(q).fetchall()
			res = [i[0] for i in res] + [i[1] for i in res]
			return res

	def get_submenu(self, cur_step, lang):
		with self.connection:
			q = """ SELECT catalog.dir_name_{0}
 					FROM (SELECT * FROM catalog, catalog_hierarchy
						  WHERE catalog_hierarchy.menu_dir_id = catalog.id
						  AND catalog.dir_name_{0} = ?
						  AND deleted = 0) as new_table
					JOIN catalog ON catalog.id = new_table.submenu_dir_id
					AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (cur_step,)).fetchall()
			res = [i[0] for i in res]
			return res

	def get_price(self, step, lang):
		with self.connection:
			q = """ SELECT file_id FROM price_list WHERE price_name_{0} = ?""".format(lang)
			res = self.cursor.execute(q, (step,)).fetchall()
			return None if not res else res[0][0]

	def has_instruction(self, step, lang):
		with self.connection:
			q = """ SELECT COUNT(*)
 					FROM instruction_content
 					JOIN catalog
 					ON instruction_content.catalog_dir_id = catalog.id
 					WHERE catalog.dir_name_{0} = ?""".format(lang)
			res = self.cursor.execute(q, (step,)).fetchall()
			return res[0][0] != 0

	def get_instruction_message(self, step, lang):
		with self.connection:
			q = """ SELECT instruction_content.caption_text_{0}
					FROM instruction_content
					JOIN catalog ON catalog.id = instruction_content.catalog_dir_id
					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (step,)).fetchall()
			return res[0][0] if res else ''

	def get_instruction_videos(self, step, lang):
		with self.connection:
			q = """ SELECT instruction_content.video_id
					FROM instruction_content
					JOIN catalog ON catalog.id = instruction_content.catalog_dir_id
					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (step,)).fetchall()
			return [i[0] for i in res if i[0] is not None and i[0] != '']

	def get_instruction_photos(self, step, lang):
		with self.connection:
			q = """ SELECT instruction_content.picture_id
					FROM instruction_content
					JOIN catalog ON catalog.id = instruction_content.catalog_dir_id
					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (step,)).fetchall()
			return [i[0] for i in res if i[0] is not None and i[0] != '']

	def get_instruction_documents(self, step, lang):
		with self.connection:
			q = """ SELECT instruction_content.document_id
					FROM instruction_content
					JOIN catalog ON catalog.id = instruction_content.catalog_dir_id
					WHERE catalog.dir_name_{0} = ? AND catalog.deleted = 0""".format(lang)
			res = self.cursor.execute(q, (step,)).fetchall()
			return [i[0] for i in res if i[0] is not None and i[0] != '']

	def is_continued(self, uid):
		with self.connection:
			q = "SELECT COUNT(*) FROM user WHERE uid = ? AND is_continued = 1"
			res = self.cursor.execute(q, (uid,)).fetchall()
			return res[0][0] == 1

	def user_continued(self, uid):
		with self.connection:
			q = "UPDATE user SET is_continued = 1 WHERE uid = ?"
			self.cursor.execute(q, (uid,))

	def get_ru_messages(self):
		with self.connection:
			q = "SELECT id, step, lang, text FROM message"
			res = self.cursor.execute(q).fetchall()
			return res

	def is_stopped_bot(self, uid):
		with self.connection:
			q = "SELECT COUNT(*) FROM user WHERE stopped_bot = 1 AND uid = ?"
			res = self.cursor.execute(q, (uid,)).fetchall()
			return res[0][0] == 1

	def user_unblocked_bot(self, uid):
		with self.connection:
			q = "UPDATE user SET stopped_bot = 0 WHERE uid = ?"
			self.cursor.execute(q, (uid,))

	def user_blocked_bot(self, uid):
		with self.connection:
			q = "UPDATE user SET stopped_bot = 1 WHERE uid = ?"
			self.cursor.execute(q, (uid,))

	def delete_user_info(self, uid):
		with self.connection:
			q = "DELETE FROM user WHERE uid = ?"
			self.cursor.execute(q, (uid,))

	def is_admin(self, uid):
		with self.connection:
			q = "SELECT * FROM user WHERE uid = ? AND is_admin = 1"
			res = self.cursor.execute(q, (uid,)).fetchall()
			return bool(res)

	def ban_user(self, uid):
		with self.connection:
			q = "UPDATE user SET is_banned = 1 WHERE uid = ?"
			self.cursor.execute(q, (uid,))

	def is_banned(self, uid):
		with self.connection:
			q = "SELECT * FROM user WHERE uid = ? AND is_banned = 1"
			res = self.connection.execute(q, (uid,)).fetchall()
			return bool(res)

	def unban_user(self, uid):
		with self.connection:
			q = "UPDATE user SET is_banned = 0 WHERE uid = ?"
			self.cursor.execute(q, (uid,))

	# active_users_count = db.get_active_users_count()
	# blocked_bot_users_count = db.get_blocked_bot_users_count()
	# banned_users_count = db.get_banned_users_count()
	# total = db.get_total_users_count()

	def get_active_users_count(self):
		with self.connection:
			q = "SELECT COUNT(*) FROM user WHERE is_banned = 0 AND stopped_bot = 0"
			res = self.cursor.execute(q).fetchall()
			return res[0][0]

	def get_stopped_bot_users_count(self):
		with self.connection:
			q = "SELECT COUNT(*) FROM user WHERE stopped_bot = 1"
			res = self.cursor.execute(q).fetchall()
			return res[0][0]

	def get_banned_users_count(self):
		with self.connection:
			q = "SELECT COUNT(*) FROM user WHERE is_banned = 1"
			res = self.cursor.execute(q).fetchall()
			return res[0][0]

	def get_total_users_count(self):
		with self.connection:
			q = "SELECT COUNT(*) FROM user"
			res = self.cursor.execute(q).fetchall()
			return res[0][0]

	def get_users_for_excel_file(self):
		"""
		:return: list of tuples: [("user_id", "fullname", "username", "phone", "lang", "is_admin", "is_banned", "stopped_bot", "registration_date"),...]
		"""
		with self.connection:
			q = "SELECT uid, full_name, user_name, phone, language, is_admin, is_banned, stopped_bot, date FROM user"
			return self.cursor.execute(q).fetchall()

	def update_price_list(self, name, file_id):
		with self.connection:
			q = "UPDATE price_list SET file_id = ? WHERE price_name_ru = ?"
			self.cursor.execute(q, (file_id, name))

	def get_user_ids(self, date=None):
		with self.connection:
			if date is None:
				q = "SELECT uid FROM user"
				res = self.cursor.execute(q).fetchall()
				res = [i[0] for i in res]
				return res
			else:
				q = "SELECT uid FROM user WHERE date=?"
				res = self.cursor.execute(q, (date,)).fetchall()
				res = [i[0] for i in res]
				return res
