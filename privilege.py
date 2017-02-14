#!/usr/bin/env /usr/bin/python3
import config
import lang

priv_map = {}
m_conf=config.get_plgconf("privilege")

def get_priv(cmd):
	return priv_map[cmd]

def set_priv(cmd,priv):
	priv_map[cmd] = priv

import main
R = main.R
import database

def get_userpriv(user):
	ud = database.get_user_details(user)
	if ud != None:
		if ("privilege" in ud):
			return _("Username: %(username)s has privilege %(pri)i.") % {'username':user,'pri':ud["privilege"]}
	return _("Username: %s info not exist in database.") % user

def set_userpriv(user,priv):
#	if user in pluginmgr.plgmap["xmpp"].m_bot.muc_jid:
#		print(_("Redirecting user privilege change to real JID."))
#		user = pluginmgr.plgmap["xmpp"].m_bot.muc_jid[user]
	ud = database.get_user_details(user)
	cre = False
	if ud == None:
		ud={}
		cre = True
	ud["privilege"] = int(priv)
	database.set_user_details(user,ud)
	if not cre:
		return _("Set user %(username)s privilege to %(pri)i successfully.") % {'username':user,'pri':int(priv)}
	else:
		return _("Created and set user %(username)s privilege to %(pri)i successfully.") % {'username':user,'pri':int(priv)}

@R.add(_("\/setpriv\s(\S+)\s(\d+)\s?"),"oncommand")
def set_priv_msg(msg):
	try:
		cmd = msg["res"].group(1)
		cmd2 = msg["res"].group(2)
	except IndexError:
		return [(None,msg["from"])]
	return [(set_userpriv(cmd,cmd2),msg["from"])]

@R.add(_("\/getpriv\s(\S+)\s?"),"oncommand")
def get_priv_msg(msg):
	try:
		cmd = msg["res"].group(1)
	except IndexError:
		return [(None,msg["from"])]
	return [(get_userpriv(cmd),msg["from"])]

def check_priv(cmd,username):
	if cmd == None:
		print("privilege.py:check_priv: command returned None. This is a bug.")
		return False
	if not(cmd in priv_map):
		return True
	else:
		priv = 100
		if username in m_conf["trusted_jid"]:
			priv = 0
		ud = database.get_user_details(username)
		if ud != None:
			if "privilege" in ud:
				if ud["privilege"] < priv:
					priv = ud["privilege"]
			else:
				ud["privilege"] = 60
				database.set_user_details(username,ud)
		if (priv <= priv_map[cmd]):
			return True
		else:
			return False

set_priv("getpriv",2)
set_priv("setpriv",2)

R.set_help("privilege",_("""privilege system usage:
/setpriv USERNAME privilege
	Set user privilege.
/getpriv USERNAME
	Get user privilege.
"""))
