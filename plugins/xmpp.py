#!/usr/bin/env /usr/bin/python3
import sleekxmpp
import config
import main
import privilege
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
		self.muc_jid = dict()
		self.reply_to_nonmuc = True
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
		f_ind = msg['body'].find('/')
		if(f_ind != -1 and f_ind < 2):
			if main.R.has_command(msg['body']) == 1 :
				tim = self.check_time(msg['from'],False)
				if (tim[0]):
					res = self.proc_msg(msg["body"],msg)
					if not(res == None):
						self.send_message(mto=msg['from'].bare,
				                      mbody="%s" % (res),
				                      mtype='groupchat')
					else:
						self.send_message(mto=msg['from'].bare,
		                          mbody=_("Type /help HELPENTRY to get help. Leave HELPENTRY to empty to get all registered help."),
		                          mtype='groupchat')
				elif not(tim[1] == ""):
					self.send_message(mto=msg['from'].bare,
				                      mbody="%s" % (tim[1]),
				                      mtype='groupchat')
		for k in main.R.message_map:
			main.R.message_map[k](self,msg)
	def muc_presence(self, presence):
		if(presence["muc"]["jid"].bare == None):
			print(_("Warning: Cannot get real JID in mulituser chatroom, please check your room settings."))
		else:
			self.muc_jid[presence['from']] = presence["muc"]["jid"].bare
		self.roles[presence['from']] = presence['muc']['role']
	def message(self,msg):
		if self.reply_to_nonmuc:
			if msg['type'] in ('chat', 'normal'):
				f_ind = msg['body'].find('/')
				if(f_ind != -1 and f_ind < 2):
					tim = self.check_time(msg['from'],True)
					if (tim[0]):
						res = self.proc_msg(msg["body"],msg)
						if not(res == None):
							self.send_message(mto=msg['from'].bare,
					                  mbody="%s" % (res),
					                  mtype='chat')
						else:
							self.send_message(mto=msg['from'].bare,
					                  mbody=_("Type /help HELPENTRY to get help. Leave HELPENTRY to empty to get all registered help."),
					                  mtype='chat')
					elif not(tim[1] == ""):
							self.send_message(mto=msg['from'].bare,
					                  mbody="%s" % (tim[1]),
					                  mtype='chat')
					for k in main.R.message_map:
						main.R.message_map[k](self,msg)
	def proc_msg(self,msgbody,msg):
		if msg['from'].bare in lang.lang_map:
			lang.chg_loc(lang.lang_map[msg['from'].bare])
		else:
			lang.lang_map[msg['from'].bare]=lang.c_locale["default"]
			lang.chg_loc(lang.lang_map[msg['from'].bare])
		purecmd = main.R.get_purecmd(msgbody)
		if privilege.check_priv(purecmd,str(msg["from"])):
			return main.R.go_call(msgbody,msg)
		else:
			return _("%(username)s: Insufficient privileges.") % {'username':self.get_real_jid(str(msg["from"]))}
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
	def handle_probe(self, presence):
		sender = presence['from']
		if sender.bare == self.jid:
			self.reply_to_nonmuc = False
		self.sendPresence(pto=sender, pstatus="", pshow="")

	def get_real_jid(self,jid):
		if jid in self.muc_jid:
			return self.muc_jid[jid]
		else:
			return None

if "resource" in m_conf:
	m_bot = MUCBot(m_conf["jid"]+'/'+m_conf["resource"], m_conf["password"], m_conf["chatrooms"])
else:
	m_bot = MUCBot(m_conf["jid"], m_conf["password"], m_conf["chatrooms"])

if m_bot.connect():
	m_bot.auto_authorize = False
	m_bot.makePresence(pfrom=m_conf["jid"], pstatus='', pshow='')
	m_bot.sendPresence(pto=m_conf["jid"], ptype='probe')
	m_bot.process(block=False)
