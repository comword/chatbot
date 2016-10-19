#!/usr/bin/python3
import main
import pluginmgr
import config
import time,os
import lang

m_conf=config.get_plgconf("logg")
R = main.R
log_path=os.getcwd()+m_conf["path"]
plv = pluginmgr.plgmap["privilage"]
log_flag={}
ISOTIMEFORMAT='%Y-%m-%d %X'

def check_log_dir():
	if os.path.isdir(log_path):
		return True
	else:
		return False

@R.add("startlog","oncommand")
def start_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		return _("This session is being logged.")
	else:
		log_flag[orgmsg['from'].bare] = {}
		log_flag[orgmsg['from'].bare]["file"] = open(log_path+"/"+time.strftime("%Y%m%d%H%M%S", time.localtime())+orgmsg['from'].bare.split('@')[0]+".log",'w')
		log_flag[orgmsg['from'].bare]["logging"] = True
		log_flag[orgmsg['from'].bare]["sttime"] = time.localtime()
		return _("A new log started at %(time)s")% {'time':time.strftime(ISOTIMEFORMAT, time.localtime())}

@R.add("stoplog","oncommand")
def stop_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		log_flag[orgmsg['from'].bare]["file"].close()
		log_flag.pop(orgmsg['from'].bare)
		return _("The log is stopped at %(time)s") % {'time':time.strftime(ISOTIMEFORMAT, time.localtime())}
	else:
		return _("This session is not being logged.")

@R.add("pauselog","oncommand")
def pause_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		if (log_flag[orgmsg['from'].bare]["logging"] == True):
			log_flag[orgmsg['from'].bare]["logging"] = False
			return _("Current log process paused.")
		else:
			return _("This logging session is paused.")
	else:
		return _("This session is not being logged.")

@R.add("resumelog","oncommand")
def resume_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		if (log_flag[orgmsg['from'].bare]["logging"] == False):
			log_flag[orgmsg['from'].bare]["logging"] = True
			return _("Current log process resumed.")
		else:
			return _("This logging session is not paused.")
	else:
		return _("This session is not being logged.")

@R.add("lslog","oncommand")
def ls_log(msg,orgmsg):
	tmp = os.popen('ls '+"."+m_conf["path"]+"|grep " + orgmsg['from'].bare.split('@',1)[0]).readlines()
	res = ""
	for line in tmp:
		res += line
	return res
@R.add("rmlog","oncommand")
def rm_log(msg,orgmsg):
	try:
		cmd = msg[1]
		cmd = flite_command(cmd)
	except IndexError:
		return None
	

@R.add("catlog","oncommand")
def cat_log(msg,orgmsg):
	try:
		cmd = msg[1]
		cmd = flite_command(cmd)
	except IndexError:
		return None
	tmp = os.popen('cat '+"."+m_conf["path"]+"/"+ cmd +" 2>&1").readlines()
	res = ""
	for line in tmp:
		res += line
	return res

@R.add("proclog","onmessage")
def proc_log(cla,msg):
	if msg['from'].bare in log_flag:
		if(log_flag[msg['from'].bare]["logging"] == True):
			log_flag[msg['from'].bare]["file"].write(time.strftime("%H:%M:%S", time.localtime())+" "+msg['mucnick']+": "+msg["body"]+"\n")
		else:
			pass

def flite_command(cmd):
	cmd = cmd.replace('/',"")
	cmd = cmd.replace('\\',"")
	cmd = cmd.replace(';',"")
	cmd = cmd.replace(':',"")
	cmd = cmd.replace('`',"")
	cmd = cmd.replace('"',"")
	cmd = cmd.replace('\'',"")
	cmd = cmd.replace('|',"")
	cmd = cmd.replace('>',"")
	cmd = cmd.replace('<',"")
	cmd = cmd.replace('$',"")
	cmd = cmd.replace('*',"")
	return cmd

if (check_log_dir() == False):
	print (_("Log directory not exist, creating..."))
	os.makedirs(log_path)

plv.set_priv("startlog",2)
plv.set_priv("stoplog",2)
plv.set_priv("pauselog",2)
plv.set_priv("resumelog",2)
plv.set_priv("rmlog",0)
plv.set_priv("lslog",2)
