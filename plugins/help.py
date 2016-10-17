#!/usr/bin/python3
import main
import pluginmgr
R = main.R

@R.add("help","oncommand")
def show_help(msg,orgmsg):
	try:
		cmd = msg[1]
	except IndexError:
		return("Type /help (plugin) to get help. Type /listplugin to list all plugins.")
	return R.get_help(cmd)
