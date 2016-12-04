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
			if "id" in item:
				m_id = item["id"]
				if m_id in lib:
					print(_("Duplicated item id %(m_id)s in file %(file)s.") % {'m_id':m_id,'file':a_file})
					raise Exception({'m_id':m_id,'file':a_file})
				else:
					lib[m_id] = item

def lookup_lib_byid(obj_type,obj_id):
	if obj_id in lib:
		return lib[obj_id]
	else:
		return None

#load_lib()
