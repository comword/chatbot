#!/usr/bin/env /usr/bin/python3
import main
B = main.B
import lang
import config
import privilege
m_conf=config.get_plgconf("ircproto")

from irc3.plugins.command import command
from irc3.testing import ini2config
import irc3
import os
import re
import threading

@irc3.plugin
class MyPlugin:
    requires = [
        'irc3.plugins.core',
#        'irc3.plugins.userlist',
#        'irc3.plugins.command',
    ]
    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.log
        self.joinoninvite = False
#    def connection_made(self):
#        """triggered when connection is up"""

#    def server_ready(self):
#        """triggered after the server sent the MOTD (require core plugin)"""

#    def connection_lost(self):
#        """triggered when connection is lost"""
    @irc3.event(irc3.rfc.JOIN)
    def welcome(self, mask, channel, **kw):
        pass
#       Welcome people who join a channel
#        if mask.nick != self.bot.nick:
#                self.bot.privmsg(channel, 'Welcome %s!' % mask.nick)
#        else:
#                self.bot.privmsg(channel, "Hi guys!")
    @irc3.event(irc3.rfc.INVITE)
    def on_invite(self, mask=None, channel=None, **kw):
#        print(mask,channel,kw)
        if self.joinoninvite:
            self.bot.join(channel)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, data=None, **kw):
#        print(mask, data, kw["target"])
        f_ind = data.find('/')
        if (f_ind != -1 and f_ind < 2):
            target = kw["target"]
            if target in lang.lang_map:
                lang.chg_loc(lang.lang_map[target])
            else:
                lang.lang_map[target]=lang.c_locale["default"]
                lang.chg_loc(lang.lang_map[target])
#            if target[0] == '#': #msg in channel
            purecmd = main.R.get_purecmd(data)
            if privilege.check_priv(purecmd,"irc:"+mask.nick):
                main.R.go_call(self.make_orgmsg(mask,data,kw["target"]),"irc:")
            else:
                B.send_message(_("%(username)s: Insufficient privileges.") % {'username':mask.nick}, "irc:"+target)
#            else:#privmsg
#                pass

    def make_orgmsg(self,mask,data,target):
        r = dict()
        if target[0] == '#':
            r['type'] = "muc"
            r["mucroom"] = "irc:"+target
            r['mucnick'] = mask.nick
            r["from"] = "irc:"+target
        else:
            r['type'] = 'normal'
            r["from"] = "irc:"+mask.nick
        r['body'] = data
        r['realfrom'] = "irc:"+mask.nick
        return r

def irc_main():
    global ircbot
    conf = os.getcwd() + m_conf["config"]
    if os.path.isfile(conf):
        conf_f = open(conf)
        config = ini2config(conf_f.read())
        conf_f.close()
    else:
        print(_("IRC config file does not exist."))
        return
    ircbot = irc3.IrcBot.from_config(config)
    ircbot.joinoninvite = m_conf["joinoninvite"]
    ircbot.run(forever=True)

@B.defnew_protocal("dosend","irc:")
def irc_do_send(msg,to):
    rtarget = re.search("irc\:(.*)",to).group(1)
    global ircbot
    ircbot.privmsg(rtarget,msg,nowait=True)
    return True

threading.Thread(target = irc_main, args = (), name = 'thread-ircproto').start()
