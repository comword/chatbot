#!/usr/bin/env /usr/bin/python3
import main
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
#import ssl

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
            if kw["target"][0] == '#': #msg in channe
                purecmd = main.R.get_purecmd(data)
                if privilege.check_priv(purecmd,"irc:"+mask.nick):
                    l = main.R.go_call(data,self.make_orgmsg(mask,data,kw["target"]))
                else:
                    return _("%(username)s: Insufficient privileges.") % {'username':self.get_real_jid(str(msg["from"]))}
            else:#privmsg
                pass

    def make_orgmsg(mask,data,target):
        r = dict()
        r["from"] = "irc:"+mask.nick
        if target[0] == '#':
            r['type'] = "muc"
            r["mucroom"] = "irc:"+target
            r['mucnick'] = mask.nick
        else:
            r['type'] = 'normal'
        r['body'] = data
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

B = main.B
@B.defnew_protocal("dosend","irc:")
def irc_do_send(msg,to):
    global ircbot
    ircbot.send_msg(to,msg)
    return True

threading.Thread(target = irc_main, args = (), name = 'thread-ircproto').start()
