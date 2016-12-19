#!/usr/bin/env /usr/bin/python3
import os
import config
m_conf=config.get_plgconf("library")
import main
import pluginmgr
R = main.R
import json
import lang

libpath = os.getcwd()+m_conf["path"]
lib = dict()

def load_lib():
	file_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(libpath) for f in filenames if os.path.splitext(f)[1] == '.json']
	for a_file in file_list:
		tmp = open(a_file)
		m_dat = json.load(tmp)
		tmp.close()
		for item in m_dat:
			if "type" in item:
				if not item["type"] in lib:
					lib[item["type"]] = dict()
				if "id" in item:
					m_id = item["id"]
					if m_id in lib[item["type"]]:
						print(_("Duplicated item id %(m_id)s in file %(file)s, merging...") % {'m_id':m_id,'file':a_file})
						lib[item["type"]][m_id] = merge_dicts(lib[item["type"]][m_id],item)
#						print(lib[item["type"]][m_id])
#						raise Exception({'m_id':m_id,'file':a_file})
					else:
						lib[item["type"]][m_id] = item
			else:
				print(_("Type tag not found in id %(m_id)s in file %(file)s.") % {'m_id':m_id,'file':a_file})
				raise Exception({'m_id':m_id,'file':a_file})

def upd_user_info(usr_info,obj_dire):
	#already [data]
	if not obj_dire in usr_info:
		return usr_info #do nothing
	for it in usr_info[obj_dire]:
#This part get all parts from user data.
		if not isinstance(it,str):
			print(_("Bad part: "))
			print(it)
			continue
		user_part = usr_info[obj_dire][it]
		iter_user_part(usr_info,it,user_part)
		
def iter_user_part(usr_info,path,it):
	if isinstance(it,list):
		for index,item in enumerate(it):
			if isinstance(it,dict):
				if "pre-name" in it: # found a object
					des_obj = get_des_obj(it["pre-name"])
					if not des_obj == None:
						write_back(usr_info,path,des_obj)
				for key in item:
					iter_user_part(usr_info,path+'/'+index+'/'+key,it[key])
			elif isinstance(it,str):
				# deal with simplified item
				des_obj = proc_sim_str(it)
				if not des_obj == None:
					write_back(usr_info,path,des_obj)
	elif isinstance(it,dict):
		if "pre-name" in it: # found a object
			des_obj = get_des_obj(it["pre-name"])
			if not des_obj == None:
				write_back(usr_info,path,des_obj)
		else: #maybe have more struction
			for k in it:
				iter_user_part(usr_info,path+'/'+k,it[k])
#	if isinstance(it,list):
#		for index,item in enumerate(it):
#			if isinstance(item,str):
# - abc/def #str
#    ^   ^
#  type/objid
#				if item.find('/') == -1: # not a object
#					continue
#				n_id = item.split('/')[1]
#				n_type = item.split('/')[0]
#				if not n_type in lib:
#					print(_("Type %(type)s not found of object %(obj)s.") % {'type':n_type,'obj':item})
#					continue
#				if not n_id in lib[n_type]:
#					print(_("ID %(ID)s not found in type %(type)s of object %(obj)s.") % {'ID':n_ID,'type':n_type,'obj':item})
#					continue
#				des_obj = lib[n_type][n_id]
#				write_back(usr_info,path,des_obj)
#			elif isinstance(item,dict):
# - 
#    a:b
#				for key in item:
#					iter_user_part(usr_info,path+'/'+index+'/'+key,it[key])
#		return 1
#	elif isinstance(it,dict):
# a:
#		for key in it:
#			iter_user_part(usr_info,path+'/'+key,it[key])
#		return 1

def write_back(userinfo,path,info):
	path_sep = path.split('/')
	comm = "userinfo"
	for p in path_sep:
		comm += "[%s]" % p
	if eval('"pre-name" in ' + comm):
		exec(comm+".pop('pre-name')") # remove pre-name
	tmp = merge_dicts([comm,info])
	comm += " = tmp"
	exec(comm)

def merge_dicts(*dict_args):
	result = dict()
	for dic in dict_args:
		result.update(dic)
	return result

def get_des_obj(item):
	if item.find('/') == -1:
		return None
	n_id = item.split('/')[1]
	n_type = item.split('/')[0]
	if not n_type in lib:
		print(_("Type %(type)s not found of object %(obj)s.") % {'type':n_type,'obj':item})
		return None
	if not n_id in lib[n_type]:
		print(_("ID %(ID)s not found in type %(type)s of object %(obj)s.") % {'ID':n_ID,'type':n_type,'obj':item})
		return None
	des_obj = lib[n_type][n_id]
	return des_obj

def proc_sim_str(m_str):
	try:
		if m_str.find('/') == -1:
			return None
		n_type = item.split('/')[0]
		if m_str.find('|') == -1:
			n_cou = 1
			n_id = m_str.split('/')[1]
		else:
			n_cou = int(m_str.split('|',1)[1]) # may throw except
			n_id = m_str.split('|',1)[0].split('/')[1]
		if not n_type in lib:
			print(_("Type %(type)s not found of object %(obj)s.") % {'type':n_type,'obj':item})
			return None
		if not n_id in lib[n_type]:
			print(_("ID %(ID)s not found in type %(type)s of object %(obj)s.") % {'ID':n_ID,'type':n_type,'obj':item})
			return None
		des_obj = lib[n_type][n_id]
		return des_obj
	except:
		return None

@R.add(_("compluserdata"),"oncommand")
def complete_userdata(msg,orgmsg):
	try:
		user = msg[1]
	except IndexError:
		return None
	ud = pluginmgr.plgmap["database"].get_user_details(user)
	if ("data" in ud):
		res = upd_user_info(ud["data"],m_conf["def_obj_dir"])
	return res

load_lib()
