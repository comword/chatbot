#!/usr/bin/python3
import main
import config
import pluginmgr
import lang

priv_map = {}
m_conf=config.get_plgconf("privilage")
R = main.R

def get_priv(cmd):
	return priv_map[cmd]

def set_priv(cmd,priv):
	priv_map[cmd] = priv

def get_userpriv(user):
	ud = pluginmgr.plgmap["users"].get_user_details(user)
	if ("Privilage" in ud):
		return _("Username: %(username)s has privilage %(pri)i.") % {'username':user,'pri':ud["Privilage"]}
	else:
		return _("Username: %s info not exist in database.") % user

def set_userpriv(user,priv):
	ud = pluginmgr.plgmap["users"].get_user_details(user)
	if ud == None:
		return _("Username: %s info not exist in database.") % user
	ud["Privilage"] = priv
	pluginmgr.plgmap["users"].set_user_details(user,ud)
	return _("Set user %(username)s privilage to %(pri)i successfully.") % {'username':user,'pri':priv}

@R.add("setpriv","oncommand")
def set_priv_msg(msg,orgmsg):
	try:
		cmd = msg[1]
		cmd2 = msg[2]
	except IndexError:
		return None
	return set_userpriv(cmd,cmd2)

@R.add("getpriv","oncommand")
def get_priv_msg(msg,orgmsg):
	try:
		cmd = msg[1]
	except IndexError:
		return None
	return get_userpriv(cmd)
	
def check_priv(cmd,username):
	if not(cmd in priv_map):
		return True
	else:
		priv = 100
		if username in pluginmgr.plgmap["xmpp"].m_bot.roles:
			if (pluginmgr.plgmap["xmpp"].m_bot.roles[username] == "moderator"):
				priv = 2
		ud = pluginmgr.plgmap["users"].get_user_details(username)
		if ud == None:
			print(_("Username: %s info not exist in database. Creating...") % username)
			ud = dict()
			ud["Privilage"] = 60
			pluginmgr.plgmap["users"].set_user_details(username,ud)
		if ud["Privilage"]<priv:
			priv = ud["Privilage"]
		if (priv<=priv_map[cmd]):
			return True
		else:
			return False
