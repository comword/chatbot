#!/usr/bin/env /usr/bin/python3
import main
import pluginmgr
R = main.R
import lang


@R.add(_("help"),"oncommand")
def show_help(msg,orgmsg):
	try:
		cmd = msg[1]
	except IndexError:
		return _("Type /help (plugin) to get help. Type /listplugins to list all plugins.")
	return R.get_help(cmd)
