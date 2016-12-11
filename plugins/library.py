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
			if isinstance(item,str):
				if item.find('/') == -1:
					print(_("Bad object: %s.") % item)
					continue
				n_id = item.split('/')[1]
				n_type = item.split('/')[0]
				if not n_type in lib:
					print(_("Type %(type)s not found of object %(obj)s.") % {'type':n_type,'obj':item})
					continue
				if not n_id in lib[n_type]:
					print(_("ID %(ID)s not found in type %(type)s of object %(obj)s.") % {'ID':n_ID,'type':n_type,'obj':item})
					continue
				des_obj = lib[n_type][n_id]
				
			elif isinstance(item,dict):
				for key in item:
					iter_user_part(usr_info,path+'/'+index+'/'+key,it[key])
		return 1
	elif isinstance(it,dict):
		for key in it:
			iter_user_part(usr_info,path+'/'+key,it[key])
		return 1

def merge_dicts(*dict_args):
	result = dict()
	for dic in dict_args:
		result.update(dic)
	return result

load_lib()
