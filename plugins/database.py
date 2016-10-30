#/usr/bin/python3
import plyvel,os
import config
m_conf=config.get_plgconf("database")
import main
import pluginmgr
R = main.R
import json
import lang
import yaml

user_db = os.getcwd()+m_conf["user_path"]

def check_dbs():
	plyvel.DB(user_db, create_if_missing=True)

def get_user_details(uname):
	db = plyvel.DB(user_db)
	tmp=db.get(uname.encode('utf-8'))
	db.close()
	if tmp == None:
		return tmp
	else:
		return json.loads(tmp.decode('utf-8'))
def set_user_details(uname,datas):
	db = plyvel.DB(user_db)
	res = db.put(uname.encode('utf-8'),json.dumps(datas).encode('utf-8'))
	db.close()
	return res

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
	if udb == None:
		udb = get_user_details(orgmsg['from'].bare+"/"+user)
		user = orgmsg['from'].bare+"/"+user
		if(udb == None):
			return _("User: %(user)s not found in database.") % {'user':user}
	tmpdic = udb[subdic]
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
		value = msg[2]
	except IndexError:
		return None
	ud = get_user_details(user)
	if udb == None:
		return _("User %(user)s not found.") % {'user':user}
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
		return _("In %(dict)s has %(info)s") % {'dict':last_ind,'info':res} + _(" Please give more specific details.")
	else:
		operation = "udb[user]"
		for i in range(0,len(msg-3)):
			operation += "[%s]" % msg[i+2]
		operation += " = "
	return None

@R.add(_("parseyaml"),"oncommand")
def parse_yaml(msg,orgmsg):
	try:
		user = msg[1]
		yml = orgmsg["body"].split(" ",3)[3]
	except IndexError:
		return None
	try:
		datamap = yaml.safe_load(yml)
	except Exception as e:
		return "%s" % e
	ud = get_user_details(user)
	if(ud == None):
		ud={}
	ud['data']=datamap
	set_user_details(user,ud)
	return _("Set user %s data by parse YAML successfully.") % user

@R.add(_("dumpyaml"),"oncommand")
def dump_yaml(msg,orgmsg):
	try:
		user = msg[1]
		subdict = msg[2]
	except IndexError:
		return None
	udb = get_user_details(user)
	if udb == None:
		return _("Index %(ind)s not found in user %(user)s") % {'ind':subdic,'user':user}
	tmpdic = udb[user]
	last_ind = ""
	for i in range(0,len(msg-3)):
		if msg[i+2] in tmpdic:
			tmpdic = tmpdic[msg[i+2]]
			last_ind = msg[i+2]
	if isinstance(tmpdic,dict):
		return yaml.dump(tmpdic)

check_dbs()

plv = pluginmgr.plgmap["privilage"]
plv.set_priv("setuinfo",2)
plv.set_priv("getuinfo",2)
plv.set_priv("parseyaml",2)
plv.set_priv("dumpyaml",2)

R.set_help("database",_("""Database plugin usage:
/getuinfo <USER NAME> <FIRST CATALOGUE> <...>
/setuinfo <USER NAME> <FIRST CATALOGUE> <...> <DATA>
/parseyaml
/dumpyaml
"""))
