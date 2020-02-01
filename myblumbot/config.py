# -*-coding: utf-8 -*-
import logging
import os
import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.basicConfig(stream=sys.stderr, level=logging.WARN)

if os.environ.get('ENV') == 'DEV':
	TEST_CONFIG = True
elif os.environ.get('ENV') == 'PROD':
	TEST_CONFIG = False
else:
	raise ValueError("'ENV' environment variable should be 'DEV' or 'PROD'")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if TEST_CONFIG:
	token = '406265614:AAHjHg7adE8a2ocF9GwakJ6dhvf8eZBrPG8'  # @BlumUz_bot
	# token = '368421686:AAGnaXnbA9WUMM-xacTHgpPcfewELvT_yC0'  # @MyBlumBot
	database_name = os.path.join(BASE_DIR, 'BlumUz.db')
	bot_name = '@BlumUz_bot'
	#bot_name = '@MyBlumBot'
	shelve_name = os.path.join(BASE_DIR, 'States', f'{bot_name[1:]}_user_states')
	users_excel_filename = os.path.join(BASE_DIR, 'users.xlsx')
	sentry_on = False
	sentry_dns = ""
else:
	token = '368421686:AAGnaXnbA9WUMM-xacTHgpPcfewELvT_yC0'
	database_name = os.path.join(BASE_DIR, 'BlumUz.db')
	bot_name = '@MyBlumBot'
	shelve_name = os.path.join(BASE_DIR, 'States', f'{bot_name[1:]}_user_states')
	users_excel_filename = os.path.join(BASE_DIR, 'users.xlsx')
	sentry_on = True
	sentry_dns = "https://0196dc6c696344ab9e48796c1171e432@sentry.io/1858233"

languages = {'ru', 'uz'}
density = {'MДФ 18': 760, 'МДФ 16': 760, 'ДСП 18': 680, 'ДСП 16': 680,
		   'MDF 18': 760, 'MDF 16': 760, 'DSP 18': 680, 'DSP 16': 680}

height_boundaries = {
	'AVENTOS HF': {'min': 480, 'max': 1040},
	'AVENTOS HS': {'min': 350, 'max': 800},
	'AVENTOS HL': {'min': 300, 'max': 580},
	'AVENTOS HK top': {'min': 200, 'max': 600},
	'AVENTOS HK-S': {'min': 180, 'max': 400},
	'AVENTOS HK-XS': {'min': 240, 'max': 600},
	'AVENTOS HK-XS TIP-ON': {'min': 240, 'max': 600}
}
width_boundaries = {
	'AVENTOS HF': {'min': 220, 'max': 1800},
	'AVENTOS HS': {'min': 220, 'max': 1800},
	'AVENTOS HL': {'min': 220, 'max': 1800},
	'AVENTOS HK top': {'min': 220, 'max': 1800}
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
