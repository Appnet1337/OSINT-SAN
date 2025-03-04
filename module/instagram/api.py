#By bafomet
import requests
import random
import json
from module.utils import COLORS

try:
	from module import local
except ImportError:
	from . import local

resp_js = None
is_private = False
total_uploads = 12


def get_page(username):
	global resp_js
	session = requests.session()
	session.headers = {'User-Agent': random.choice(local.useragent)}
	# TODO: Судя по всему, незалогиненному юзеру нельзя забирать запросы с `__a`,
	# TODO: А я в рот ебал инстаграм, хуйня для обделенных вниманием людей,
	# TODO: но решить проблему надо, да
	resp_js = session.get(
		f'https://www.instagram.com/{username}/',
		params={"__a": "1"},
		allow_redirects=False,
	).text
	return resp_js


def exinfo():

	def xprint(xdict, text):
		if xdict:
			print(f"{COLORS.GNSL} [ {COLORS.REDL}Часто использует{COLORS.GNSL} ] {text} :")
			print()
			i = 0
			for key, val in xdict.items():
				if len(mails) == 1:
					if key in mails[0]:
						continue
				print(f"  {local.gr}{key} : {local.wh}{val}")
				i += 1
				if i > 4:
					break
			print()
		else:
			pass
	
	raw = local.find(resp_js)

	mails = raw['email']
	tags = local.sort_list_with_counter(raw['tags'])
	ment = local.sort_list_with_counter(raw['mention'])

	if mails:
		if len(mails) == 1:
			print(f"{COLORS.GNSL} [ {COLORS.REDL}Часто использует{COLORS.GNSL} ]: {mails[0]}")
			print()
		else:
			print(f"{COLORS.GNSL} [ {COLORS.REDL}Часто использует{COLORS.GNSL} ]: 5")
			print()
			for mail in mails:
				print(mail)

			print()

	xprint(tags, "Теги")
	xprint(ment, "Упоминание в сообщении или публикации владельца страницы")


def user_info(usrname):

	global total_uploads, is_private
	
	resp_js = get_page(usrname)
	js = json.loads(resp_js)
	js = js['graphql']['user']
	
	if js['is_private'] is True:
		is_private = True
	
	if js['edge_owner_to_timeline_media']['count'] > 12:
		pass
	else:
		total_uploads = js['edge_owner_to_timeline_media']['count']

	usrinfo = {
		f' {COLORS.WHSL}Имя профиля{COLORS.GNSL}       ': js['username'],
		f' {COLORS.REDL}ID Профиля{COLORS.GNSL}        ': js['id'],
		f' {COLORS.WHSL}Имя{COLORS.GNSL}               ': js['full_name'],
		f' {COLORS.WHSL}Подписчики{COLORS.GNSL}        ': js['edge_followed_by']['count'],
		f' {COLORS.WHSL}Он подписан{COLORS.GNSL}       ': js['edge_follow']['count'],
		f' {COLORS.WHSL}Сообщения Картинки{COLORS.GNSL}': js['edge_owner_to_timeline_media']['count'],
		f' {COLORS.WHSL}Сообщения видео{COLORS.GNSL}   ': js['edge_felix_video_timeline']['count'],
		f' {COLORS.WHSL}reels{COLORS.GNSL}             ': js['highlight_reel_count'],
		f' {COLORS.WHSL}bio                ': js['biography'].replace('\n', ', '),
		f' {COLORS.REDL}Внешний URL        ': js['external_url'],
		f' {COLORS.WHSL}Приват             ': js['is_private'],
		f' {COLORS.WHSL}Верификация        ': js['is_verified'],
		f' {COLORS.REDL}Фото профиля       ': local.urlshortner(js['profile_pic_url_hd']),
		f' {COLORS.WHSL}Бизнес аккаунт     ': js['is_business_account'],
		#'connected to fb': js['connected_fb_page'],  -- requires login
		f' {COLORS.WHSL}Присоединился      ': js['is_joined_recently'],
		f' {COLORS.WHSL}Бизнес каталог     ': js['business_category_name'],
		f' {COLORS.WHSL}Категория          ': js['category_enum'],
		f' {COLORS.WHSL}has guides         ': js['has_guides'],
	}

	print(f"{COLORS.GNSL} [ {COLORS.REDL} Информация о запрашиваемом профиле{COLORS.GNSL} ]")
	print()
	for key, val in usrinfo.items():
		print(f"{key} : {val}")

	print("")

	exinfo()





def highlight_post_info(i):
	global resp_js

	postinfo = {}
	total_child = 0
	child_img_list = []

	x = json.loads(resp_js)
	js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']

	# this info will be same on evry post
	info = {
		'  comments': js['edge_media_to_comment']['count'],
		'  comment disable': js['comments_disabled'],
		'  timestamp': js['taken_at_timestamp'],
		'  likes': js['edge_liked_by']['count'],
		'  location': js['location'],
	}

	# if image dosen't have caption this key dosen't exist instead of null
	try:
		info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
	except IndexError:
		pass

	# if uploder has multiple images / vid in single post get info how much edges are
	if 'edge_sidecar_to_children' in js:
		total_child = len(js['edge_sidecar_to_children']['edges'])

		for child in range(total_child):
			js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']['edge_sidecar_to_children']['edges'][child]['node']
			img_info = {
				'  typename': js['__typename'],
				'  id': js['id'],
				'  shortcode': js['shortcode'],
				'  dimensions': str(js['dimensions']['height'] + js['dimensions']['width']),
				'  image url' : js['display_url'],
				'  fact check overall': js['fact_check_overall_rating'],
				'  fact check': js['fact_check_information'],
				'  gating info': js['gating_info'],
				'  media overlay info': js['media_overlay_info'],
				'  is_video': js['is_video'],
				'  accessibility': js['accessibility_caption']
			}

			child_img_list.append(img_info)

		postinfo['imgs'] = child_img_list
		postinfo['info'] = info

	else:
		info = {
			'  comments': js['edge_media_to_comment']['count'],
			'  comment disable': js['comments_disabled'],
			'  timestamp': js['taken_at_timestamp'],
			'  likes': js['edge_liked_by']['count'],
			'  location': js['location'],
		}

		try:
			info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
		except IndexError:
			pass

		img_info = {
				'  typename': js['__typename'],
				'  id': js['id'],
				'  shortcode': js['shortcode'],
				'  dimensions': str(js['dimensions']['height'] + js['dimensions']['width']),
				'  image url' : js['display_url'],
				'  fact check overall': js['fact_check_overall_rating'],
				'  fact check': js['fact_check_information'],
				'  gating info': js['gating_info'],
				'  media overlay info': js['media_overlay_info'],
				'  is_video': js['is_video'],
				'  accessibility': js['accessibility_caption']
			}
		
		child_img_list.append(img_info)
		
		postinfo['imgs'] = child_img_list
		postinfo['info'] = info

	return postinfo


def post_info():
	
	if is_private is True:
		print(f"{local.fa} {local.gr}cannot use -p for private accounts !\n")
		exit(1)
	
	posts = []
	
	for x in range(total_uploads):
		posts.append(highlight_post_info(x))

	for x in range(len(posts)):
		# get 1 item from post list
		print(f"{local.su}{local.re} post %s :" % x)
		for key, val in posts[x].items():
			if key == 'imgs':
				# how many child imgs post has
				postlen = len(val)
				# loop over all child img
				print(f"{local.su}{local.re} contains %s media" % postlen)
				for y in range(postlen):
					# print k,v of all child img in loop
					for xkey, xval in val[y].items():
						print(f"  {local.gr}{xkey} : {local.wh}{xval}")
			if key == 'info':
				print(f"{local.su}{local.re} info :")
				for key, val in val.items():
					print(f"  {local.gr}{key} : {local.wh}{val}")
				print("")
