#!/usr/bin/env /usr/bin/python3
import plyvel,os
import config
m_conf=config.get_plgconf("database")
import main
R = main.R
import json
import lang
import yaml

user_db = os.getcwd()+m_conf["user_path"]

def check_dbs():
	db = plyvel.DB(user_db, create_if_missing=True)
	for key, value in db:
		if key == b'':
			db.delete("".encode("utf-8"),sync = True)

def get_user_details(uname):
	db = plyvel.DB(user_db)
	tmp = db.get(uname.encode('utf-8'))
	db.close()
	if tmp == None:
		return None
	else:
		return json.loads(tmp.decode('utf-8'))

def set_user_details(uname,datas):
	db = plyvel.DB(user_db)
	res = db.put(uname.encode('utf-8'),json.dumps(datas).encode('utf-8'))
	db.close()
	return res

def try_user_poss(user,perfix):
	udb = get_user_details(user)
	if udb == None:
		udb = get_user_details(perfix+"/"+user)
		user = perfix+"/"+user
		if udb == None:
			return user,dict()
		else:
			return user,udb
	else:
		return user,udb

@R.add(_("\/geturoot\s(\S+)\s?"),"oncommand")
def getu_root(groups,orgmsg):
	try:
		user = groups.group(1)
	except IndexError:
		return None
	userf,udb = try_user_poss(user,orgmsg['from'].bare)
	if(not udb):
		return _("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf}
	res = list()
	for k in udb:
		res.append(k)
	return res

@R.add(_("\/createuser\s(\S+)\s?"),"oncommand")
def create_user(groups,orgmsg):
	try:
		username = groups.group(1)
	except:
		return None
	#check user existence
	udb = get_user_details(username)
	if udb != None:
		return _("User %s already existed.") % username
	udb = dict()
	udb["Privilage"] = 60
	set_user_details(username,udb)
	return _("User %s created successfully.") % username

@R.add(_("\/getuinfo\s(\S+)\s(\w+)\s?(.*)"),"oncommand")
def getu_info(groups,orgmsg):
	try:
		user = groups.group(1)
		subdic = groups.group(2)
		msg = groups.group(3)
#/getuinfo <username> <firstdir>
#		0		1			2
	except IndexError:
		return None
	userf,udb = try_user_poss(user,orgmsg['from'].bare)
	if(not udb):
		return _("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf}
	if subdic in udb:
		tmpdic = udb[subdic]
	else:
		return _("Directory %s can't be found in user database.") % subdic
	if not isinstance(tmpdic,dict):
		return _("Result: %(res)s") % {'res':(tmpdic)}
	last_ind = subdic
	msg = msg.split(' ')
	for i in range(0,len(msg)):
		if msg[i] in tmpdic:
			tmpdic = tmpdic[msg[i]]
			last_ind = msg[i]
	if isinstance(tmpdic,dict):
		res = []
		for k in tmpdic:
			res.append(k)
		return _("In %(dict)s has %(info)s") % {'dict':last_ind,'info':res}
	else:
		return _("Result: %(res)s") % {'res':(tmpdic)}

@R.add(_("\/setuinfo\s(\w+)\s(.*?)\s*\|((.|\n)*)?"),"oncommand")
def setu_info(groups,orgmsg):
	try:
		user = groups.group(1)
		value = groups.group(3)
		msg = groups.group(2).split(' ')
	except IndexError:
		return None
	userf,udb = try_user_poss(user,orgmsg['from'].bare)
	if not udb:
		return _("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf}
	tmpdic = udb
	last_ind = ""
	for i in range(0,len(msg)):
		if msg[i] in tmpdic:
			tmpdic = tmpdic[msg[i]]
			last_ind = msg[i]
	if isinstance(tmpdic,dict):
		res = []
		for k in tmpdic:
			res.append(k)
		return _("In %(dict)s has %(info)s") % {'dict':last_ind,'info':res} + _(" Please give more specific details.")
	else:
		operation = "udb"
		for i in range(0,len(msg)):
			operation += "[\"%s\"]" % msg[i]
		operation += " = "
		operation += "\"%s\"" % value
		exec(operation)
		set_user_details(user,udb)
	return operation

@R.add(_("\/parseyaml\s(.+?)\s((.|\n)*)"),"oncommand")
def parse_yaml(groups,orgmsg):
	try:
		user = groups.group(1)
		yml = groups.group(2)
	except IndexError:
		return None
	try:
		datamap = yaml.safe_load(yml)
	except Exception as e:
		return "%s" % e
	userf,udb = try_user_poss(user,orgmsg['from'].bare)
	if(not udb):
		return _("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf}
	udb['data'] = datamap
	set_user_details(user,ud)
	return _("Set user %s data by parse YAML successfully.") % user

@R.add(_("\/dumpyaml\s(.+?)\s(\w+)\s?(.*)?"),"oncommand")
def dump_yaml(groups,orgmsg):
	try:
		user = groups.group(1)
		subdict = groups.group(2)
	except IndexError:
		return None
	userf,udb = try_user_poss(user,orgmsg['from'].bare)
	if not udb:
		return _("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf}
	if subdict in udb:
		tmpdic = udb[subdict]
	else:
		return _("Index %(index)s cannot be found in user %(user)s.") % {'user':user,'index':subdict}
	try:
		msg = groups.group(3).split(" ")
	except:
		msg = []
	for i in range(0,len(msg)):
		if msg[i] in tmpdic:
			tmpdic = tmpdic[msg[i]]
	if isinstance(tmpdic,dict):
		return yaml.dump(tmpdic,allow_unicode=True)
	else:
		return tmpdic

@R.add(_("\/listuserdbk\s?"),"oncommand")
def list_userdbk(groups,orgmsg):
	db = plyvel.DB(user_db)
	res = list()
	for key, value in db:
		res.append(key.decode("utf-8"))
	return res

@R.add(_("\/deluserdbk\s((.|\n)*)"),"oncommand")
def del_userdbk(groups,orgmsg):
	try:
		user = groups.group(1)
	except IndexError:
		return None
	db = plyvel.DB(user_db)
	db.delete(user.encode("utf-8"),sync = True)
	return _("Delete user %s successfully.") % user

check_dbs()

import privilage

privilage.set_priv("geturoot",0)
privilage.set_priv("setuinfo",2)
privilage.set_priv("getuinfo",2)
privilage.set_priv("parseyaml",2)
privilage.set_priv("dumpyaml",2)
privilage.set_priv("listuserdbk",0)
privilage.set_priv("deluserdbk",0)

R.set_help("database",_("""Database plugin usage:
/getuinfo USERNAME FIRSTCATALOGUE <...>
/setuinfo USERNAME FIRSTCATALOGUE <...>|<DATA>
/parseyaml USERNAME YAML
	This parse YAML document to USERNAME/data
/dumpyaml USERNAME FIRSTCATALOGUE <...>
/listuserdbk
	List all user available in database.
/deluserdbk
	Remove a user in database.
"""))
