#/usr/bin/python3
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

def get_lib_bytype(obj_type):
	if obj_type in lib:
		return lib[obj_type]
	else:
		return None

def get_obj_byid(obj_id,lib):
	if obj_id in lib:
		return lib[obj_id]
	else:
		return None

def upd_user_info(usr_info,obj_dire):
	#already [data]
	if not obj_dire in usr_info:
		return usr_info #do nothing
	for it in usr_info[obj_dire]:
		if not it.find('/')==-1:
			pass

def merge_dicts(*dict_args):
	result = dict()
	for dic in dict_args:
		result.update(dic)
	return result

load_lib()
