# -*-coding: utf-8 -*-

TEST_CONFIG = 0

if TEST_CONFIG:
	token = '406265614:AAHjHg7adE8a2ocF9GwakJ6dhvf8eZBrPG8' # @BlumUz_bot
	# token = '368421686:AAGnaXnbA9WUMM-xacTHgpPcfewELvT_yC0'  # @MyBlumBot
	database_name = '../BlumUz.db'
	bot_name = '@BlumUz_bot'
	# bot_name = '@MyBlumBot'
	shelve_name = './States/{0}_user_states'.format(bot_name[1:])
	users_excel_filename = "../users.xlsx"
else:
	token = '368421686:AAGnaXnbA9WUMM-xacTHgpPcfewELvT_yC0'
	database_name = '/usr/share/nginx/html/BlumUz/BlumUz.db'
	bot_name = '@MyBlumBot'
	shelve_name = '/usr/share/nginx/html/BlumUz/Bot/States/{0}_user_states'.format(bot_name[1:])
	users_excel_filename = "/usr/share/nginx/html/BlumUz/users.xlsx"

languages = {'ru', 'uz'}
density = {'MДФ 18': 760, 'МДФ 16': 760, 'ДСП 18': 680, 'ДСП 16': 680,
		   'MDF 18': 760, 'MDF 16': 760, 'DSP 18': 680, 'DSP 16': 680}

height_boundaries = {
	'AVENTOS HF': {'min': 480, 'max': 1040},
	'AVENTOS HS': {'min': 350, 'max': 800},
	'AVENTOS HL': {'min': 300, 'max': 580},
	'AVENTOS HK': {'min': 200, 'max': 600},
	'AVENTOS HK-S': {'min': 180, 'max': 400},
	'AVENTOS HK-XS': {'min': 240, 'max': 600},
	'AVENTOS HK-XS TIP-ON': {'min': 240, 'max': 600}
}
width_boundaries = {
	'AVENTOS HF': {'min': 220, 'max': 1800},
	'AVENTOS HS': {'min': 220, 'max': 1800},
	'AVENTOS HL': {'min': 220, 'max': 1800},
	'AVENTOS HK': {'min': 220, 'max': 1800}
}

mechanism_with_height_parameter = ('AVENTOS HL', 'AVENTOS HS')
mechanism_with_lever = ('AVENTOS HF', 'AVENTOS HL')

hl_lever_values_for_x_y = {'20L3200': 153,
						   '20L3500': 203,
						   '20L3800': 253,
						   '20L3900': 303}

admin_nicknames = ['@TalipovZ', '@saaanjik']

posting_file_types = ['document', 'photo', 'video', 'audio', 'sticker', 'location']
caption_limit = 195
