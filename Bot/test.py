# -*-coding: utf-8 -*-

from shelver import Shelver
import utils
from sqlighter import SQLighter
#with SQLighter() as db:
# 	#print(db.get_final_catalog_directories())
# 	#print(db.get_products())
# 	#print(db.get_caption('AVENTOS Hs', 'ru'))
# 	#print(db.get_photos('AVENTOS HF', 'ru'))
# 	#print(db.get_videos('AVENTOS HF', 'ru'))
# 	#print(db.is_in_submenu('Подъёмные механизмы', 'AVENTOS HF', 'ru'))
# 	#print(db.get_submenu('Подъёмные механизмы', 'ru'))
# 	#print(db.has_instruction('CLIP top BLUMOTION', 'ru'))
# 	#print(db.get_instruction_videos('CLIP top', 'ru'))
# 	#print(db.get_instruction_documents('CLIP top', 'ru'))
# 	#print(db.get_instruction_photos('CLIP top', 'r'))
# 	#print(db.has_instruction('asd', 'ru'))
# 	#print(db.is_stopped_bot('123'))
# 	pass
#
# # with Shelver().conn as states:
# # 	uid = '3235063'
# # 	for i in states:
# # 		print(i, ": ", states[i])
# # 	del states[uid]
# # 	for i in states:
# # 		print(i, ": ", states[i])
#
# def test_round_func():
# 	with SQLighter() as db:
# 		# height = 480
# 		# coef = 5
# 		# aventos = 'AVENTOS HS'
# 		# print(db.get_recomendation_mechanism_hs_hl(height, coef, aventos))
#
# 		test_height = {
# 			799: 800,
# 			745: 745,
# 			743: 745,
# 			742: 740,
# 			740: 740,
# 			676: 676,
# 			677: 676,
# 			675: 675,
# 			674: 675,
# 			672: 670,
# 			531: 530,
# 			533: 535,
# 			527: 526,
# 			526: 526,
# 			524: 525,
# 			350: 350,
# 			352: 350
# 		}
# 		for test in test_height:
# 			assert utils.round_height(test) == test_height[test], \
# 				"Test not passed. Arg: {0}, FuncAns: {1}, ShouldBe: {2}".format(test, utils.round_height(test),
# 																				test_height[test])
with Shelver().conn as states:
	#print((db.has_instruction('Kargo', lang='uz') and 'Kargo' in db.finaly_dirs()) \
	for i in states:
		print(i, states[i])
	for i in states:
		del states[i]
	for i in states:
		print(i, states[i])
	print("END")
#
# def test_1():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		if uid in states:
# 			del states[uid]
#
# 		db.delete_user_info(uid)
#
# def test_2():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		if uid in states:
# 			del states[uid]
#
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m')
#
# def test_3():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		if uid in states:
# 			del states[uid]
#
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m', lang='ru')
#
# def test_4():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		if uid in states:
# 			del states[uid]
#
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m', lang='ru', phone='123123123')
#
#
# def test_5():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur':'lang_menu', 'path': ['lang_menu']}
# 		db.delete_user_info(uid)
#
# def test_6():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 		db.delete_user_info(uid)
#
# def test_7():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 		db.delete_user_info(uid)
#
# def test_8():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
# 		db.delete_user_info(uid)
#
# def test_9():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur':'lang_menu', 'path': ['lang_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m')
#
# def test_10():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m')
#
# def test_11():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m')
#
# def test_12():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m')
#
# def test_13():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m', lang='ru')
#
#
# def test_14():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m', lang='ru')
#
#
# def test_15():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m', lang='ru')
#
#
# def test_16():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
# 		db.delete_user_info(uid)
# 		db.save_user_info(uid, 'Маткурбанов Алишер', 'alisher_m', lang='ru')
#
# def test_17():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'lang_menu', 'path': ['lang_menu']}
#
# def test_18():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'send_phone_menu', 'path': ['send_phone_menu']}
#
# def test_19():
# 	uid = '3235063'
# 	with SQLighter() as db, Shelver().conn as states:
# 		states[uid] = {'cur': 'main_menu', 'path': ['main_menu']}
#
# #Test 1: Not in shelver, not in db
# #Test 2: Not in shelver, have no lang
# #Test 3: Not in shelver, have no phone
# #Test 4: Not in shelver, all have
#
# #Test 5: In shelver - state - lang_menu, not in db
# #Test 6: In shelver - state - phone_send_menu contact, not in db
# #Test 7: In shelver - state - phone_send_menu text, not in db
# #Test 8: In shelver - state - main_menu, not in db
#
# #Test 9: In shelver - state - lang_menu, have no lang
# #Test 10: In shelver - state - phone_send_menu contact, have no lang
# #Test 11: In shelver - state - phone_send_menu text, have no lang
# #Test 12: In shelver - state - main_menu, have no lang
#
# #Test 13: In shelver - state - lang_menu, have no phone
# #Test 14: In shelver - state - phone_send_menu contact, have no phone
# #Test 15: In shelver - state - phone_send_menu text, have no phone
# #Test 16: In shelver - state - main_menu, have no phone
#
# #Test 17:
#
#
# #test_1() #DONE
# #test_2()
# #test_3()
# #test_4()
# #test_5()
# #test_6()
# #test_7()
# #test_8()
# #test_9()
# #test_10()
# #test_11()
# #test_12()
# #test_13()
# #test_14()
# #test_15()
# #test_16()
# #test_17()
# #test_18()
# #test_19()
	
#	def print_states():
		# with Shelver(shelve_name='./States/MyBlumBot_user_states (2)').conn as states:
		# 	states.clear()
		# 	for i in states:
		# 		print(i,":",states[i])
#	print(db.get_active_users_count())
#	print(db.get_stopped_bot_users_count())
#	print(db.get_banned_users_count())


	