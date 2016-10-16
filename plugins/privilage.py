#!/usr/bin/python3
import main
import config
import pluginmgr

priv_map = {}
m_conf=config.get_plgconf("privilage")
R = main.R

def get_priv(cmd):
	return priv_map[cmd]

def set_priv(cmd,priv):
	priv_map[cmd] = priv

def check_priv(cmd,username):
	priv = 100
	if username in pluginmgr.plgmap["xmpp"].m_bot.roles:
		if (pluginmgr.plgmap["xmpp"].m_bot.roles[username] == "moderator"):
			priv = 2
	if not(cmd in priv_map):
		return True
	else:
		if (priv<=priv_map[cmd]):
			return True
		else:
			return False
