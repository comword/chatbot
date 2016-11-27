#!/usr/bin/python3
import sleekxmpp
import config
import main
import pluginmgr
import time
import lang

m_conf=config.get_plgconf("xmpp")
xmpp_priv = {}
xmpp_priv["moderator"] = 2
xmpp_priv["participant"] = 4
refractory_p=m_conf["refractory"]
refr_alert={}
last_time = dict()

class MUCBot(sleekxmpp.ClientXMPP):
	def __init__(self, jid, password, roomlist):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.roles = dict()
		self.roomlist = roomlist
		self.add_event_handler("message", self.message)
		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("groupchat_presence", self.muc_presence)
#		self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
#		self.add_event_handler("muc::%s::got_offline" % self.room, self.muc_offline)
#		self.add_event_handler("muc::%s::message" % self.room, self.muc_message)
		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0199') # XMPP Ping
	def start(self, event):
		self.get_roster()
		self.send_presence()
		for room in self.roomlist:
			if "password" in room:
				self.plugin['xep_0045'].joinMUC(room["room"],room["nick"],password=room["password"],wait=True)
			else:
				self.plugin['xep_0045'].joinMUC(room["room"],room["nick"],wait=True)
	def muc_message(self, msg):
#		nick = self.find_nick(msg["from"].bare)
#		if msg['mucnick'] != nick:
#			tofind = nick+": "
#			if not(msg['body'].find(tofind) == -1):
#				tim = self.check_time(msg['from'],False)
#				if (tim[0]):
#					subm = msg['body'][msg['body'].find(tofind):]
#					res = self.proc_msg(subm,msg)
#					if not(res == None):
#						self.send_message(mto=msg['from'].bare,
#				                      mbody="%s" % (res),
#				                      mtype='groupchat')
#					else:
#						self.send_message(mto=msg['from'].bare,
#		                          mbody=_("Type /help (plugin) to get help. Type /listplugins to list all plugins."),
#		                          mtype='groupchat')
#				elif not(tim[1] == ""):
#					self.send_message(mto=msg['from'].bare,
#				                      mbody="%s" % (tim[1]),
#				                      mtype='groupchat')
		f_ind = msg['body'].find('/')
		if(f_ind != -1 and f_ind < 2):
			if main.R.has_command(msg['body'].split("/",1)[1].split(' ',1)[0]) == 1 :
				tim = self.check_time(msg['from'],False)
				if (tim[0]):
					res = self.proc_msg(msg["body"],msg)
					if not(res == None):
						self.send_message(mto=msg['from'].bare,
				                      mbody="%s" % (res),
				                      mtype='groupchat')
					else:
						self.send_message(mto=msg['from'].bare,
		                          mbody=_("Type /help (plugin) to get help. Type /listplugins to list all plugins."),
		                          mtype='groupchat')
				elif not(tim[1] == ""):
					self.send_message(mto=msg['from'].bare,
				                      mbody="%s" % (tim[1]),
				                      mtype='groupchat')
		for k in main.R.message_map:
			main.R.message_map[k](self,msg)
	def muc_presence(self, presence):
		nick = presence['from']
		self.roles[nick] = presence['muc']['role']
	def message(self,msg):
		if msg['type'] in ('chat', 'normal'):
			tim = self.check_time(msg['from'],True)
			if (tim[0]):
				res = self.proc_msg(msg["body"],msg)
				if not(res == None):
					self.send_message(mto=msg['from'].bare,
		                          mbody="%s" % (res),
		                          mtype='chat')
				else:
					self.send_message(mto=msg['from'].bare,
		                          mbody=_("Type /help (plugin) to get help. Type /listplugins to list all plugins."),
		                          mtype='chat')
			elif not(tim[1] == ""):
					self.send_message(mto=msg['from'].bare,
		                          mbody="%s" % (tim[1]),
		                          mtype='chat')
			for k in main.R.message_map:
				main.R.message_map[k](self,msg)
	def proc_msg(self,subm,msg):
		if msg['from'].bare in lang.lang_map:
			lang.chg_loc(lang.lang_map[msg['from'].bare])
		else:
			lang.lang_map[msg['from'].bare]=lang.c_locale["default"]
			lang.chg_loc(lang.lang_map[msg['from'].bare])
		cmd = subm[subm.find("/"):]
		cmd = cmd.split(" ",1)[0][1:]
		if(pluginmgr.plgmap["privilage"].check_priv(cmd,str(msg["from"]))):
			func = main.R.get_command(cmd)
			if isinstance(func,str):
				return func
			else:
				return func(subm[subm.find("/"):].split(),msg)
		else:
			return _("%(username)s: Insufficient privileges.") % {'username':msg["from"]}
	def check_time(self,user,ischat):
		if user in last_time:
			if user in refractory_p:
				ref = refractory_p[user]
			elif user in self.roles:
				if self.roles[user] in refractory_p:
					ref = refractory_p[self.roles[user]]
			elif ischat:
				ref = refractory_p["<CHAT>"]
			else:
				ref = refractory_p["<OTHER>"]
			if(time.time()>last_time[user]+ref):
				return True,""
			else:
				if refr_alert[user] == False :
					refr_alert[user]=True
					return False,_("Don't use this bot too frequently. %(user)s cool time is %(sec)i second.") % {'user':user,'sec':ref}
				else:
					return False,""
		else:
			last_time[user] = time.time()
			refr_alert[user] = False
			return True,""

	def find_nick(self,room):
		for it in self.roomlist:
			if room == it["room"]:
				return it["nick"]
		return False

m_bot = MUCBot(m_conf["jid"], m_conf["password"], m_conf["chatrooms"])

def start_xmpp():
	if m_bot.connect():
		return m_bot
