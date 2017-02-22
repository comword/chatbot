#!/usr/bin/env /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import telegram
from telegram.error import NetworkError, Unauthorized

import main
B = main.B
import lang
import config
import privilege
import plyvel,os
m_conf=config.get_plgconf("telegram")
tg_db = os.getcwd()+m_conf["database"]

import threading
import re

if not 'token' in m_conf:
    raise Exception(_("Token not found in the configure file."))

class tg_bot():
    def __init__(self):
        self.update_id = None
        self.bot = telegram.Bot(m_conf["token"])

    def msg_proc(self):
        updates = self.bot.getUpdates(offset=self.update_id,timeout=10)
        for u in updates:
            self.update_id = u.update_id + 1
            print(u)
            set_database_uid(u.message.from_user.username,u.message.from_user.id)
            #self.make_orgmsg(u.message.from_user,u.message.text)

    def make_orgmsg(self,from_u,data):
        r = dict()
        if target[0] == '#':
            r['type'] = "muc"
            r["mucroom"] = "tg:"+target
            r['mucnick'] = mask.nick
            r["from"] = "tg:"+target
        else:
            r['type'] = 'normal'
            r["from"] = "tg:"+mask.nick
        r['body'] = data
        r['realfrom'] = "tg:"+mask.nick
        return r

def tg_main():
    global tgbot_ins
    tgbot_ins = tg_bot()
    while True:
        try:
            tgbot_ins.msg_proc()
        except NetworkError:
            pass
        except Unauthorized:
            self.update_id += 1


@B.defnew_protocal("dosend","tg:")
def tg_do_send(msg,to):
    rtarget = re.search("tg\:(.*)",to).group(1)
    global tgbot_ins
    m_id = get_database_uid(rtarget)
    if m_id == None:
        return False
    tgbot_ins.bot.sendMessage(chat_id=m_id, text=msg)
    return True

if not os.path.exists(tg_db):
	os.makedirs(tg_db)
db = plyvel.DB(tg_db, create_if_missing=True)
db.close()

def get_database_uid(username):
    db = plyvel.DB(tg_db)
    tmp = db.get(username.encode('utf-8'))
    db.close()
    if tmp == None:
        return None
    else:
        return int(tmp)

def set_database_uid(username,uid):
    db = plyvel.DB(tg_db)
    res = db.put(username.encode('utf-8'),str(uid).encode('utf-8'))
    db.close()
    return res

threading.Thread(target = tg_main, args = (), name = 'thread-tgproto').start()
