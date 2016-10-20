#!/usr/bin/python3
import plyvel,os
import config
m_conf=config.get_plgconf("users")
import main
R = main.R
import json
import lang

user_db = os.getcwd()+m_conf["db_path"]+"/users.db"

def check_dbs():
	plyvel.DB(user_db, create_if_missing=True)
def get_user_details(uname):
	db = plyvel.DB(user_db)
	tmp=db.get(uname.encode('utf-8'))
	if tmp == None:
		return tmp
	else:
		return json.loads(tmp.decode('utf-8'))
def set_user_details(uname,datas):
	db = plyvel.DB(user_db)
	return db.put(uname.encode('utf-8'),json.dumps(datas).encode('utf-8'))

@R.add(_("getuinfo"),"oncommand")
def getu_info(msg,orgmsg):
	try:
		user = msg[1]
		subdic = msg[2]
#/getuinfo <username> <firstdir>
#		0		1			2
	except IndexError:
		return None
	udb = get_user_details(user)
	if not user in udb:
		if orgmsg['from'].bare+"/"+user in udb:
			user = orgmsg['from'].bare+"/"+user
		else:
			return _("User: %(user)s not found in database.") % {'user':user}
	tmpdic = udb[user]
	last_ind = ""
	for i in range(0,len(msg-3)):
		if msg[i+2] in tmpdic:
			tmpdic = tmpdic[msg[i+2]]
			last_ind = msg[i+2]
	if isinstance(tmpdic,dict):
		res = []
		for k in tmpdic:
			res.append(k)
		return _("In %(dict)s has %(info)s") % {'dict':last_ind,'info':res}
	else:
		return _("Result: %(res)s") % {'res':(tmpdic)}

@R.add(_("setuinfo"),"oncommand")
def setu_info(msg,orgmsg):
	try:
		user = msg[1]
	except IndexError:
		return None
	return None

check_dbs()
