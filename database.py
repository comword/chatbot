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
def getu_root(msg):
	try:
		user = msg["res"].group(1)
	except IndexError:
		return None,msg["from"]
	userf,udb = try_user_poss(user,msg['mucroom'])
	if(not udb):
		return _("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf},msg["from"]
	res = list()
	for k in udb:
		res.append(k)
	return [(res,msg["from"])]

@R.add(_("\/createuser\s(\S+)\s?"),"oncommand")
def create_user(msg):
	try:
		username = msg["res"].group(1)
	except:
		return [(None,msg["from"])]
	#check user existence
	udb = get_user_details(username)
	if udb != None:
		return [(_("User %s already existed.") % username,msg["from"])]
	udb = dict()
	udb["privilege"] = 60
	set_user_details(username,udb)
	return [(_("User %s created successfully.") % username,msg["from"])]

@R.add(_("\/getuinfo\s(\S+)\s(\w+)\s?(.*)"),"oncommand")
def getu_info(msg):
	try:
		user = msg["res"].group(1)
		subdic = msg["res"].group(2)
		msg = msg["res"].group(3)
#/getuinfo <username> <firstdir>
#		0		1			2
	except IndexError:
		return [(None,msg["from"])]
	userf,udb = try_user_poss(user,msg['mucroom'])
	if(not udb):
		return [(_("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf},msg["from"])]
	if subdic in udb:
		tmpdic = udb[subdic]
	else:
		return [(_("Directory %s can't be found in user database.") % subdic,msg["from"])]
	if not isinstance(tmpdic,dict):
		return [(_("Result: %(res)s") % {'res':(tmpdic)},msg["from"])]
	last_ind = subdic
	msg = msg.split(' ')
	for i in range(0,len(msg)):
		try:
			tmpdic = tmpdic[msg[i]]
			last_ind = msg[i]
		except:
			return [(_("A error happend during accessing key %s. Please check your input.") % msg[i],msg["from"])]
	if isinstance(tmpdic,dict):
		res = []
		for k in tmpdic:
			res.append(k)
		return [(_("In %(dict)s has %(info)s") % {'dict':last_ind,'info':res},msg["from"])]
	else:
		return [(_("Result: %(res)s") % {'res':(tmpdic)},msg["from"])]

@R.add(_("\/setuinfo\s(\S+)\s(.*?)\s*\|((.|\n)*)?"),"oncommand")
def setu_info(msg):
	try:
		user = msg["res"].group(1)
		value = msg["res"].group(3)
		msg = msg["res"].group(2).split(' ')
	except IndexError:
		return [(None,msg["from"])]
	userf,udb = try_user_poss(user,msg['mucroom'])
	if not udb:
		return [(_("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf},msg["from"])]
	tmpdic = udb
	last_ind = ""
	if msg[0] == "Privilege":
		return [(_("Don't use this function to change privilege."),msg["from"])]
	for i in range(0,len(msg)):
		try:
			tmpdic = tmpdic[msg[i]]
			last_ind = msg[i]
		except:
			return [(_("A error happend during accessing key %s. Please check your input.") % msg[i],msg["from"])]
	if isinstance(tmpdic,dict):
		res = []
		for k in tmpdic:
			res.append(k)
		return [(_("In %(dict)s has %(info)s") % {'dict':last_ind,'info':res} + _(" Please give more specific details."),msg["from"])]
	else:
		#TODO:remove exec command
		operation = "udb"
		for i in range(0,len(msg)):
			operation += "[\"%s\"]" % msg[i]
		operation += " = "
		operation += "\"%s\"" % value
		exec(operation)
		set_user_details(user,udb)
	return [(operation,msg["from"])]

@R.add(_("\/parseyaml\s(.+?)\s((.|\n)*)"),"oncommand")
def parse_yaml(msg):
	try:
		user = msg["res"].group(1)
		yml = msg["res"].group(2)
	except IndexError:
		return [(None,msg["from"])]
	try:
		datamap = yaml.safe_load(yml)
	except Exception as e:
		return [("%s" % e,msg["from"])]
	userf,udb = try_user_poss(user,msg['mucroom'])
	if(not udb):
		return [(_("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf},msg["from"])]
	udb['data'] = datamap
	set_user_details(user,ud)
	return [(_("Set user %s data by parse YAML successfully.") % user,msg["from"])]

@R.add(_("\/dumpyaml\s(.+?)\s(\w+)\s?(.*)?"),"oncommand")
def dump_yaml(msg):
	try:
		user = msg["res"].group(1)
		subdict = msg["res"].group(2)
	except IndexError:
		return [(None,msg["from"])]
	userf,udb = try_user_poss(user,msg['mucroom'])
	if not udb:
		return [(_("Either user %(user)s or user %(userf)s not found in database.") % {'user':user,'userf':userf},msg["from"])]
	if subdict in udb:
		tmpdic = udb[subdict]
	else:
		return [(_("Index %(index)s cannot be found in user %(user)s.") % {'user':user,'index':subdict},msg["from"])]
	try:
		msg = groups.group(3).split(" ")
	except:
		msg = []
	for i in range(0,len(msg)):
		if msg[i] in tmpdic:
			tmpdic = tmpdic[msg[i]]
	if isinstance(tmpdic,dict):
		return [(yaml.dump(tmpdic,allow_unicode=True),msg["from"])]
	else:
		return [(tmpdic,msg["from"])]

@R.add(_("\/listuserdbk\s?"),"oncommand")
def list_userdbk(msg):
	db = plyvel.DB(user_db)
	res = list()
	for key, value in db:
		res.append(key.decode("utf-8"))
	return [(res,msg["from"])]

@R.add(_("\/deluserdbk\s((.|\n)*)"),"oncommand")
def del_userdbk(msg):
	try:
		user = msg["res"].group(1)
	except IndexError:
		return [(None,msg["from"])]
	db = plyvel.DB(user_db)
	db.delete(user.encode("utf-8"),sync = True)
	return [(_("Delete user %s successfully.") % user,msg["from"])]

check_dbs()

import privilege

privilege.set_priv("geturoot",0)
privilege.set_priv("setuinfo",2)
privilege.set_priv("getuinfo",2)
privilege.set_priv("parseyaml",2)
privilege.set_priv("dumpyaml",2)
privilege.set_priv("listuserdbk",0)
privilege.set_priv("deluserdbk",0)

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
