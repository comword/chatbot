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
m_conf=config.get_plgconf("telegram")

import threading

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
    return True

threading.Thread(target = tg_main, args = (), name = 'thread-tgproto').start()
