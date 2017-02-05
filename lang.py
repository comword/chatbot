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
else:
	current_locale, encoding = locale.getdefaultlocale()
	def_lang=gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[current_locale])
def_lang.install()

import main
R = main.R
@R.add(_("\/listlangs\s?"),"oncommand")
def list_langs(groups,orgmsg):
	file_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(os.getcwd()+c_locale["locale"]+"/") for f in filenames if os.path.splitext(f)[1] == '.mo']
	file_list.sort()
	languages = [path.split('/')[-3] for path in file_list]
	return languages

@R.add(_("\/setlocale\s(\S+)\s?"),"oncommand")
def change_locale(groups,orgmsg):
	try:
		la = groups.group(1)
	except IndexError:
		return None
	try:
		newlang = gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[la])
		newlang.install()
	except FileNotFoundError as e:
		return "%s" % e
	lang_map[orgmsg['from'].bare]=la
	R.refresh_command_map_lang()
	return _("Language %(la)s applied successfully.") % {'la':la}

def chg_loc(locale):
	try:
		newlang = gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[locale])
		newlang.install()
	except FileNotFoundError as e:
		return "%s" % e
	R.refresh_command_map_lang()
