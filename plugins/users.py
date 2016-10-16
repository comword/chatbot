#!/usr/bin/python3
import plyvel,os
import config
m_conf=config.get_plgconf("users")

user_db = os.getcwd()+m_conf["db_path"]+"/users.db"

def check_dbs():
    plyvel.DB(user_db, create_if_missing=True)
def get_user_details(uname):
	db = plyvel.DB(user_db)
	return db.get(uname)
def set_user_details(uname,datas):
	db = plyvel.DB(user_db)
	return db.put(uname,datas)

check_dbs()
