#!/usr/bin/env /usr/bin/python3
import main
import privilege
import config

import time,os
import lang
import gzip
import tarfile
import re

m_conf=config.get_plgconf("logg")
R = main.R
log_path=os.getcwd()+m_conf["path"]
log_flag={}
ISOTIMEFORMAT='%Y-%m-%d %X'

def check_log_dir():
	if os.path.isdir(log_path):
		return True
	else:
		return False

def go_gzip(s,d):
	buf = b""
	if os.path.isfile(s):
		with open(s, 'rb') as f:
			buf += f.read()
		with gzip.open(d, 'wb') as f:
			f.write(buf)
		return 0
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
	log_files = [f for f in os.listdir(os.getcwd()+m_conf["path"]) if os.path.isfile(os.path.join(os.getcwd()+m_conf["path"], f))]
	log_files.sort()
	res = list()
	for f in log_files:
		f_date = os.path.basename(f)[0:8]
		if f_date == date:
			res.append(f)
	if len(res) != 0:
		mergegzfile(log_path,res,res[0])

def tar_reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo

def tarlog_range(orgmsg, log_path, datefrom, dateto, filename):
	if not os.path.isdir(log_path):
		return -1
	log_files = [f for f in os.listdir(os.getcwd()+m_conf["path"]) if os.path.isfile(os.path.join(os.getcwd()+m_conf["path"], f))]
	log_files.sort()
	if orgmsg['type'] == 'muc':
		log_files = [ x for x in log_files if orgmsg['mucroom'].split('@',1)[0] in x ]
	compress_list = list()
	res = "Compressed:\n"
	for f in log_files:
		f_date = os.path.basename(f)[0:8]
		if(f_date<=dateto) and (f_date>=datefrom):
			compress_list.append(os.getcwd()+m_conf["path"]+"/"+f)
			res += (f+'\n')
	tar = tarfile.open(filename, "w")
	for name in compress_list:
		tar.add(name, filter=tar_reset, arcname=os.path.basename(name))
	tar.close()
	return res

@R.add(_(".*\:\s?\/startlog\s?"),"oncommand")
def start_log(msg):
	if not msg['type'] == 'muc':
		return [(_("The log can only be operated in mulituser chat."),msg["from"])]
	if msg['mucroom'] in log_flag:
		return [(_("This session is being logged."),msg["from"])]
	else:
		log_flag[msg['mucroom']] = {}
		log_flag[msg['mucroom']]['ignore_char'] = ''
		log_flag[msg['mucroom']]["filename"] = log_path+"/"+time.strftime("%Y%m%d%H%M%S", time.localtime())+msg['mucroom'].split('@')[0]+".log"
		log_flag[msg['mucroom']]["file"] = open(log_flag[msg['mucroom']]["filename"],'w')
		log_flag[msg['mucroom']]["logging"] = True
		log_flag[msg['mucroom']]["sttime"] = time.localtime()
		return [(_("A new log started at %(time)s")% {'time':time.strftime(ISOTIMEFORMAT, time.localtime())},msg["from"])]

@R.add(_(".*\:\s?\/stoplog\s?"),"oncommand")
def stop_log(msg):
	if not msg['type'] == 'muc':
		return [(_("The log can only be operated in mulituser chat."),msg["from"])]
	if msg['mucroom'] in log_flag:
		log_flag[msg['mucroom']]["file"].close()
		go_gzip(log_flag[msg['mucroom']]["filename"],log_flag[msg['mucroom']]["filename"]+".gz")
		os.remove(log_flag[msg['mucroom']]["filename"])
		log_flag.pop(msg['mucroom'])
		return [(_("The log is stopped at %(time)s") % {'time':time.strftime(ISOTIMEFORMAT, time.localtime())},msg["from"])]
	else:
		return [(_("This session is not being logged."),msg["from"])]

@R.add(_(".*\:\s?\/pauselog\s?"),"oncommand")
def pause_log(msg):
	if not msg['type'] == 'muc':
		return [(_("The log can only be operated in mulituser chat."),msg["from"])]
	if msg['mucroom'] in log_flag:
		if (log_flag[msg['mucroom']]["logging"] == True):
			log_flag[msg['mucroom']]["logging"] = False
			return [(_("Current log process paused."),msg["from"])]
		else:
			return [(_("This logging session is paused."),msg["from"])]
	else:
		return [(_("This session is not being logged."),msg["from"])]

@R.add(_(".*\:\s?\/resumelog\s?"),"oncommand")
def resume_log(msg):
	if not msg['type'] == 'muc':
		return [(_("The log can only be operated in mulituser chat."),msg["from"])]
	if msg['mucroom'] in log_flag:
		if (log_flag[msg['mucroom']]["logging"] == False):
			log_flag[msg['mucroom']]["logging"] = True
			return [(_("Current log process resumed."),msg["from"])]
		else:
			return [(_("This logging session is not paused."),msg["from"])]
	else:
		return [(_("This session is not being logged."),msg["from"])]

@R.add(_(".*\:\s?\/lslog\s?"),"oncommand")
def ls_log(msg):
	log_files = [f for f in os.listdir(os.getcwd()+m_conf["path"]) if os.path.isfile(os.path.join(os.getcwd()+m_conf["path"], f))]
	log_files.sort()
	if msg['type'] == 'muc':
		log_files = [ x for x in log_files if msg['mucroom'].split('@',1)[0] in x ]
	if len(log_files) == 0:
		return [(_("No available log to show."),msg["from"])]
	else:
		res = ""
		for i in log_files:
			res += i
			res += '\n'
		return [(res,msg["from"])]

@R.add(_(".*\:\s?\/catlog\s(\S+)\s?"),"oncommand")
def cat_log(msg):
	try:
		cmd = msg["res"].group(1)
		cmd = fliter_command(cmd)
	except IndexError:
		return [(None,msg["from"])]
	if not os.path.isfile(os.getcwd()+m_conf["path"]+'/'+cmd):
		return [(_("File %s not found.") % cmd,msg["from"])]
	buf = ""
	with gzip.open(os.getcwd()+m_conf["path"]+'/'+cmd, 'rb') as f:
		buf += f.read().decode("utf-8")
		buf += '\n'
	return [(buf,msg["from"])]

@R.add(_(".*\:\s?\/setignore\s(\S+)\s?"),"oncommand")
def set_ignore(msg):
	if not msg['type'] == 'muc':
		return [(_("The log can only be operated in mulituser chat."),msg["from"])]
	if msg['mucroom'] in log_flag:
		if(log_flag[msg['mucroom']]["logging"] == True):
			try:
				cmd = msg["res"].group(1)
			except IndexError:
				log_flag[msg['mucroom']]["ignore_char"] = ''
				return [(_("Ignore regex removed successfully."),msg["from"])]
			try:
				re.compile(cmd)
			except:
				return [(_("Regex test failed."),msg["from"])]
			log_flag[msg['mucroom']]["ignore_char"] = cmd
			return [(_("Set ignore regex to %s successfully.") % cmd,msg["from"])]
	return [(_("This session is not being logged."),msg["from"])]

@R.add(_(".*\:\s?\/tarfile\s(\d+)\s(\d+)\s(\S+)\s?"),"oncommand")
def gen_file(msg):
	try:
		datefrom = msg["res"].group(1)
		dateto = msg["res"].group(2)
	except IndexError:
		return [(None,msg["from"])]
	try:
		filename = msg["res"].group(3)
	except IndexError:
		filename = log_path+"/"+time.strftime("%Y%m%d%H%M%S", time.localtime())+msg['mucroom'].split('@')[0]+".tar"
	return [(tarlog_range(msg,log_path, datefrom, dateto, filename),msg["from"])]

@R.add("proclog","onmessage")
def proc_log(msg):
	if not msg['type'] == 'muc':
		return [(None,None)]
	if msg['mucroom'] in log_flag:
		if(log_flag[msg['mucroom']]["logging"] == True):
			if(check_ign(log_flag[msg['mucroom']]["ignore_char"],msg["body"])):
				log_flag[msg['mucroom']]["file"].write(time.strftime("%H:%M:%S", time.localtime())+" "+msg['mucnick']+": "+msg["body"]+"\n")
				log_flag[msg['mucroom']]["file"].flush()
	return [(None,None)]

def fliter_command(cmd):
	cmd = cmd.replace('/',"")
	cmd = cmd.replace('\\',"")
	cmd = cmd.replace(';',"")
#	cmd = cmd.replace(':',"")
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
	res = re.search(ignore_str,msg)
	if res == None:
		return True
	else:
		return False

if (check_log_dir() == False):
	print (_("Log directory not exist, creating..."))
	os.makedirs(log_path)

privilege.set_priv("startlog",2)
privilege.set_priv("stoplog",2)
privilege.set_priv("pauselog",2)
privilege.set_priv("resumelog",2)
privilege.set_priv("lslog",2)
privilege.set_priv("catlog",2)
privilege.set_priv("setignore",2)

R.set_help("logg",_("""Log bot usage:
/startlog	Start a new log session.
/stoplog	Stop current log session.
/pauselog	Pause current log session.
/resumelog	Resume paused log session.
/lslog	List all logs.
/catlog <LOGNAME>	Show log.
/setignore <IGNORE CHAR> A message started with this character won't be included in log. Leave second parameter to empty to accept all message. IGNORE CHAR format should be separated by ` e.g: (`{`< , then ( { < will be ignored.
/tarfile
"""))
