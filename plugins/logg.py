#!/usr/bin/python3
import main
import pluginmgr
import config
import time,os
import lang
import subprocess
import gzip

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

def go_gzip(s,d):
	if os.path.isfile(s):
		cmd = 'cat %s | gzip > %s' % (s,d)
		p = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
		return p.wait()
	else:
		return -1

def mergegzfile(path,f_name_list, dest_f_name):
	buf = ""
	for i in f_name_list:
		if not os.path.isfile(path+'/'+i):
			return -1
		with gzip.open(path+'/'+i, 'rb') as f:
			buf += f.read()
			buf += '\n'
	with gzip.open(path+'/'+dest_f_name, 'wb') as f:
		f.write(content)
	return 0

def mergelogperday(date, log_path):
	#date %Y%m%d
	if not os.path.isdir(log_path):
		return -1
	tmp = subprocess.Popen('ls '+log_path+"|grep gz",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	res = list()
	for l in tmp.stdout.readlines():
		f_date = os.path.basename(l.decode("utf-8"))[0:8]
		if f_date == date:
			res.append(l.decode("utf-8"))
	mergegzfile(log_path,res,tmp.stdout.readlines()[0])
	return 0

def tarlog_range(log_path, datefrom, dateto, filename):
	if not os.path.isdir(log_path):
		return -1
	if orgmsg['type'] in ('chat', 'normal'):
		tmp = subprocess.Popen('ls '+"."+m_conf["path"]+"|grep gz",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	else:
		tmp = subprocess.Popen('ls '+"."+m_conf["path"]+"|grep gz"+"|grep " + orgmsg['from'].bare.split('@',1)[0],shell=True, stdout=subprocess.PIPE)
	command = 'tar -cvf '+filename+" -C " + log_path + ' '
	for l in tmp.stdout.readlines():
		f_date = os.path.basename(l.decode("utf-8"))[0:8]
		if(f_date<=dateto) and (f_date>=datefrom):
			command += l.decode("utf-8")
	tmp = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	res = _("Compressed:\n")
	for l in tmp.stdout.readlines():
		res += l.decode("utf-8")
	return res

@R.add(_("startlog"),"oncommand")
def start_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		return _("This session is being logged.")
	else:
		log_flag[orgmsg['from'].bare] = {}
		log_flag[orgmsg['from'].bare]['ignore_char'] = ''
		log_flag[orgmsg['from'].bare]["filename"] = log_path+"/"+time.strftime("%Y%m%d%H%M%S", time.localtime())+orgmsg['from'].bare.split('@')[0]+".log"
		log_flag[orgmsg['from'].bare]["file"] = open(log_flag[orgmsg['from'].bare]["filename"],'w')
		log_flag[orgmsg['from'].bare]["logging"] = True
		log_flag[orgmsg['from'].bare]["sttime"] = time.localtime()
		return _("A new log started at %(time)s")% {'time':time.strftime(ISOTIMEFORMAT, time.localtime())}

@R.add(_("stoplog"),"oncommand")
def stop_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		log_flag[orgmsg['from'].bare]["file"].close()
		go_gzip(log_flag[orgmsg['from'].bare]["filename"],log_flag[orgmsg['from'].bare]["filename"]+".gz")
		os.remove(log_flag[orgmsg['from'].bare]["filename"])
		log_flag.pop(orgmsg['from'].bare)
		return _("The log is stopped at %(time)s") % {'time':time.strftime(ISOTIMEFORMAT, time.localtime())}
	else:
		return _("This session is not being logged.")

@R.add(_("pauselog"),"oncommand")
def pause_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		if (log_flag[orgmsg['from'].bare]["logging"] == True):
			log_flag[orgmsg['from'].bare]["logging"] = False
			return _("Current log process paused.")
		else:
			return _("This logging session is paused.")
	else:
		return _("This session is not being logged.")

@R.add(_("resumelog"),"oncommand")
def resume_log(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		if (log_flag[orgmsg['from'].bare]["logging"] == False):
			log_flag[orgmsg['from'].bare]["logging"] = True
			return _("Current log process resumed.")
		else:
			return _("This logging session is not paused.")
	else:
		return _("This session is not being logged.")

@R.add(_("lslog"),"oncommand")
def ls_log(msg,orgmsg):
	if orgmsg['type'] in ('chat', 'normal'):
		tmp = subprocess.Popen('ls '+"."+m_conf["path"]+"|grep gz",shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	else:
		tmp = subprocess.Popen('ls '+"."+m_conf["path"]+"|grep gz"+"|grep " + orgmsg['from'].bare.split('@',1)[0],shell=True, stdout=subprocess.PIPE)
	res = ""
	for l in tmp.stdout.readlines():
		res+=l.decode("utf-8")
	if res=="":
		return _("No available log to show.")
	return res

@R.add(_("rmlog"),"oncommand")
def rm_log(msg,orgmsg):
	try:
		cmd = msg[1]
		cmd = fliter_command(cmd)
	except IndexError:
		return None
	if orgmsg['type'] in ('chat', 'normal'):
		tmp = subprocess.Popen('rm -rf '+"."+m_conf["path"]+"/"+cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	else:
		if(cmd.find(orgmsg['from'].bare.split('@',1)[0])==-1):
			return _("No available log to remove.")
		tmp = subprocess.Popen('rm -rf '+"."+m_conf["path"]+"/"+cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	res = ""
	if not tmp.stderr == None:
		for l in tmp.stderr.readlines():
			res+=l.decode("utf-8")
	else:
		for l in tmp.stdout.readlines():
			res+=l.decode("utf-8")
	return res

@R.add(_("catlog"),"oncommand")
def cat_log(msg,orgmsg):
	try:
		cmd = msg[1]
		cmd = fliter_command(cmd)
	except IndexError:
		return None
	tmp = subprocess.Popen('zcat '+"."+m_conf["path"]+"/"+ cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	res = ""
	if not tmp.stderr == None:
		for l in tmp.stderr.readlines():
			res+=l.decode("utf-8")
	else:
		for l in tmp.stdout.readlines():
			res+=l.decode("utf-8")
	return res

@R.add(_("setignore"),"oncommand")
def set_ignore(msg,orgmsg):
	if orgmsg['from'].bare in log_flag:
		if(log_flag[orgmsg['from'].bare]["logging"] == True):
			try:
				cmd = msg[1]
			except IndexError:
				log_flag[orgmsg['from'].bare]["ignore_char"] = ''
				return _("Ignore character removed successfully.")
			if(len(cmd) == 1):
				log_flag[orgmsg['from'].bare]["ignore_char"] = cmd
			elif not (cmd.find('`') == -1):
				chars = cmd.split('`')
				for i in chars:
					if len(i)>1:
						return _("The length of each ignore character should be one.")
				log_flag[orgmsg['from'].bare]["ignore_char"] = cmd
			else:
				return _("The length of ignore character should be one.")
			return _("Set ignore character to %s successfully.") % cmd
	return _("This session is not being logged.")		

@R.add(_("tarfile"),"oncommand")
def gen_file(msg,orgmsg):
	try:
		datefrom = msg[1]
		dateto = msg[2]
	except IndexError:
		return None
	try:
		filename = msg[3]
	except IndexError:
		filename = log_path+"/"+time.strftime("%Y%m%d%H%M%S", time.localtime())+orgmsg['from'].bare.split('@')[0]+".tar"
	return tarlog_range(log_path, datefrom, dateto, filename)

@R.add("proclog","onmessage")
def proc_log(cla,msg):
	if msg['from'].bare in log_flag:
		if(log_flag[msg['from'].bare]["logging"] == True):
			if(check_ign(log_flag[msg['from'].bare]["ignore_char"],msg["body"])):
				log_flag[msg['from'].bare]["file"].write(time.strftime("%H:%M:%S", time.localtime())+" "+msg['mucnick']+": "+msg["body"]+"\n")
				log_flag[msg['from'].bare]["file"].flush()

def fliter_command(cmd):
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
	cmd = cmd.replace('..',"")
	return cmd

def check_ign(ignore_str,msg):
	if(ignore_str == ''):
		return True
	if(ignore_str.find('`') == -1 and len(ignore_str) == 1):
		if(msg.find(ignore_str) == -1):
			return True
		elif(msg.find(ignore_str) >= 2):
			return True
		return False
	if not (ignore_str.find('`') == -1):
		chars = ignore_str.split('`')
		for i in chars:
			if(msg.find(i) >= 0 and msg.find(i) < 2):
				return False
		return True
	return True

if (check_log_dir() == False):
	print (_("Log directory not exist, creating..."))
	os.makedirs(log_path)

plv.set_priv("startlog",2)
plv.set_priv("stoplog",2)
plv.set_priv("pauselog",2)
plv.set_priv("resumelog",2)
plv.set_priv("rmlog",0)
plv.set_priv("lslog",2)
plv.set_priv("setignore",2)

R.set_help("logg",_("""Log bot usage:
/startlog	Start a new log session.
/stoplog	Stop current log session.
/pauselog	Pause current log session.
/resumelog	Resume paused log session.
/lslog	List all logs.
/catlog <LOGNAME>	Show log.
/rmlog <LOGNAME>	Remove log.
/setignore <IGNORE CHAR> A message started with this character won't be included in log. Leave second parameter to empty to accept all message. IGNORE CHAR format should be separated by ` e.g: (`{`< , then ( { < will be ignored.
/tarfile 
"""))
