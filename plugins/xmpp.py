#!/usr/bin/python3
import pluginmgr
import sleekxmpp
import config
import logging

m_conf=config.get_plgconf("xmpp")
command_map = {}

class MUCBot(sleekxmpp.ClientXMPP):
	def __init__(self, jid, password, room, nick):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.room = room
		self.nick = nick
		self.add_event_handler("session_start", self.start)
#		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
		self.add_event_handler("muc::%s::got_offline" % self.room, self.muc_offline)
		self.add_event_handler("muc::%s::message" % self.room, self.muc_message)
		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0199') # XMPP Ping
	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        # If a room password is needed, use:
                                        # password=the_room_password,
                                        wait=True)
	def muc_message(self, msg):
		if msg['mucnick'] != self.nick:
			tofind = "@"+self.nick+" "
			if not(msg['body'].find(tofind) == -1):
				subm = msg['body'][msg['body'].find(tofind):]
				for k in command_map:
					command_map[k](msg)
	def muc_online(self, presence):
		pass
	def muc_offline(self, presence):
		pass
def register(*args):
	def decorator(f):
		f.register = tuple(args)
		command_map[tuple(args)[0]] = f
		return f
	return decorator

m_bot = MUCBot(m_conf["jid"], m_conf["password"], m_conf["chatroom"][0]["room"], m_conf["chatroom"][0]["nick"])

def start_xmpp():
	if m_bot.connect():
		return m_bot
