#!/usr/bin/env /usr/bin/python3
import os
import config
m_conf=config.get_plgconf("library")
import main
import pluginmgr
R = main.R
import json
import lang
import uuid

libpath = os.getcwd()+m_conf["path"]
lib = dict()
pcpy = ["name","id","type"]

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
					else:
						lib[item["type"]][m_id] = item
			else:
				print(_("Type tag not found in id %(m_id)s in file %(file)s.") % {'m_id':m_id,'file':a_file})
				raise Exception({'m_id':m_id,'file':a_file})

def check_user_obj_enum(usr_info,enum_d):
	if not enum_d in usr_info:
		return usr_info
	m_list = usr_info[enum_d]
	for index,item in enumerate(m_list):
		if isinstance(item,dict):
#			if "pre-name" in item:
			if "pre-name" in item and "UUID" not in item: # found a not prepared object
				des_obj = get_des_obj(item["pre-name"])
				if des_obj == None:
					print(_("Object %s not found in library.") % item["pre-name"])
				else:
					item.pop("pre-name")
					usr_info[enum_d][index] = part_copy(item,des_obj,pcpy)
		elif isinstance(item,str):
			des_obj = get_des_obj(item)
			if not des_obj == None:		
				usr_info[enum_d][index] = part_copy(dict(),des_obj,pcpy)
			else:
				print(_("Object %s not found in library.") % item)
	return usr_info

def merge_dicts(*dict_args):
	result = dict()
	for dic in dict_args:
		result.update(dic)
	return result

def part_copy(it,obj,li):
	for k in li:
		it[k] = obj[k]
	it["UUID"] = uuid.uuid4()
	return it

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

def write_back(userinfo,path,info):
	path_sep = path.split('/')
	comm = "userinfo"
	for p in path_sep:
		comm += "[%s]" % p
#	if eval('"pre-name" in ' + comm):
#		exec(comm+".pop('pre-name')") # remove pre-name
	tmp = merge_dicts([comm,info])
	comm += " = tmp"
	exec(comm)

def refine_inventory(usr_dic):
	c_enum = m_conf["def_obj_enum"]
	c_inve = m_conf["def_obj_dir"]
	for it in usr_dic[c_inve]:
		iter_check_dic(usr_dic,usr_dic[c_inve][it],it)

def get_item_enum_by_uuid(UUID,dic):
	if not isinstance(dic,list):
		return None
	for i in dic:
		if isinstance(dic[i],dict):
			if "UUID" in dic[i]:
				if dic[i]["UUID"] == UUID:
					return dic[i]
	return None

def iter_check_dic(u_dic,it,path):
	c_enum = m_conf["def_obj_enum"]
	if isinstance(it,list):
		for index,item in enumerate(it):
			res = iter_check_dic(u_dic,item,path+"/"+index)
			if res != 0:
				return -1
		return 0
	elif isinstance(it,dict):
		if "index" in it:
			if 0 <= it["index"] < len(u_dic[c_enum]):#valid then update UUID
				if not "UUID" in u_dic[c_enum][it["index"]]:
					print(_("UUID not persent in object %s.") % u_dic[c_enum][it["index"]])
					return -1
				it["UUID"] = u_dic[c_enum][it["index"]]["UUID"]
				it.pop("index")
				write_back(u_dic,path,it)
		elif "UUID" in it:#have a check
			tmp = get_item_enum_by_uuid(it["UUID"],u_dic[c_enum])
			if tmp == None:
				print(_("UUID %(UUID)s required by inventory not found in list.") % {"UUID":it["UUID"]})
				return -1
		else:
			for k in it:
				res = iter_check_dic(u_dic,it[k],path+"/"+k)
				if res != 0:
					return -1
		return 0

@R.add(_("genuserdata"),"oncommand")
def complete_userdata(msg,orgmsg):
	try:
		user = msg[1]
	except IndexError:
		return None
	ud = pluginmgr.plgmap["database"].get_user_details(user)
	if ("data" in ud):
		res = check_user_obj_enum(ud["data"],m_conf["def_obj_enum"])
		ud["data"] = res
		pluginmgr.plgmap["database"].set_user_details(user,ud)
		return _("Updated user %s data successfully.") % user
#		return res

load_lib()
