#!/usr/bin/python3
import gettext
import locale
import babel
import os
import config

appname = config.datamap["appname"]
c_locale=config.get_plgconf("languages")
gettext.bindtextdomain(appname, os.getcwd()+c_locale["locale"]+"/")
gettext.textdomain(appname)

if "default" in c_locale:
	def_lang=gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[c_locale["default"]])
else:
	current_locale, encoding = locale.getdefaultlocale()
	def_lang=gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[current_locale])
def_lang.install()

import main
R = main.R
@R.add("listlangs","oncommand")
def list_langs(msg,orgmsg):
	messagefiles = gettext.find(appname, localedir=os.getcwd()+c_locale["locale"]+"/" ,languages=babel.Locale('en').languages.keys(),all=True)
	messagefiles.sort()
	languages = [path.split('/')[-3] for path in messagefiles]
	#langlist = zip(languages, [babel.Locale.parse(lang).display_name for lang in languages])
	return languages

@R.add("changelocale","oncommand")
def change_locale(msg,orgmsg):
	try:
		la = msg[1]
	except IndexError:
		return None
	try:
		newlang = gettext.translation(appname, os.getcwd()+c_locale["locale"]+"/", languages=[la])
		newlang.install()
	except FileNotFoundError as e:
		return "%s" % e
	return _("Language %(la)s applied successfully.") % {'la':la}

