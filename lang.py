#!/usr/bin/env /usr/bin/python3
import gettext
import locale
import os
import config

appname = config.datamap["appname"]
c_locale=config.get_plgconf("languages")
gettext.bindtextdomain(appname, os.getcwd()+c_locale["locale"]+"/")
gettext.textdomain(appname)
lang_map=dict()

if "default" in c_locale:
	def_lang=gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[c_locale["default"]])
	cur_loc = c_locale["default"]
else:
	current_locale, encoding = locale.getdefaultlocale()
	def_lang=gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[current_locale])
	cur_loc = current_locale
def_lang.install()

import main
R = main.R
@R.add(_("\/listlangs\s?"),"oncommand")
def list_langs(msg):
	file_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.getcwd()+c_locale["locale"]+"/") for f in filenames if os.path.splitext(f)[1] == '.mo']
	file_list.sort()
	languages = [path.split('/')[-3] for path in file_list]
	return [(languages,msg["from"])]

@R.add(_("\/setlocale\s(\S+)\s?"),"oncommand")
def change_locale(msg):
	try:
		la = msg["res"].group(1)
	except IndexError:
		return [(None,msg["from"])]
	try:
		newlang = gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[la])
		newlang.install()
	except FileNotFoundError as e:
		return "%s" % e
	if msg["type"] == 'muc':
		lang_map[msg["mucroom"]]=la
	else:
		lang_map[msg["from"]]=la
	R.refresh_command_map_lang()
	cur_loc = la
	return [(_("Language %(la)s applied successfully.") % {'la':la},msg["from"])]

def chg_loc(locale):
	global cur_loc
	if cur_loc == locale:
		return
	try:
		newlang = gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[locale])
		newlang.install()
	except FileNotFoundError as e:
		return "%s" % e
	R.refresh_command_map_lang()
	cur_loc = locale

R.set_help("language",_("""Language settings:
/listlangs
	list all available languages.
/setlocale LANGUAGE
	switch between languages."""))
