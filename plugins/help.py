#!/usr/bin/python3
import main
import pluginmgr
R = main.R

@R.add("help","oncommand")
def show_help(msg,orgmsg):
	try:
		cmd = msg[1]
	except IndexError:
		return("Type /help (plugin) to get help. Type /listplugins to list all plugins.")
	return R.get_help(cmd)

#@R.add("manual","oncommand")
#def show_manual(msg,orgmsg):
#	try:
#		cmd = msg[1:]
#	except IndexError:
#		return("Type /help (plugin) to get help. Type /listplugins to list all plugins. Type /manual to show manual.")
#	return R.get_manual(cmd)
