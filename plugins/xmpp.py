#!/usr/bin/env /usr/bin/python3
import sleekxmpp
import config
import main
import privilege
import time
import lang
import re

m_conf=config.get_plgconf("xmpp")
xmpp_priv = {}
xmpp_priv["moderator"] = 2
xmpp_priv["participant"] = 4
refractory_p=m_conf["refractory"]
refr_alert={}
last_time = dict()
B = main.B

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
					self.proc_msg(self.build_msg(msg))
#					try:
#						for res,to in l:
#							if not to == None:
#								target,mtype=self.get_target(to)
#								if not(res == None):
#									self.send_message(mto=target,mbody="%s" % (res),mtype=mtype)
#								else:
#									self.send_message(mto=target,mbody=_("Type /help HELPENTRY to get help. Leave HELPENTRY to empty to get all registered help."), mtype=mtype)
#					except:
#						print(_("An error happened during processing return values."))
#						print(l)
#				elif not(tim[1] == ""):
#					self.send_message(mto=msg['from'].bare,mbody="%s" % (tim[1]),mtype='groupchat')
#			else:
#				self.send_message(mto=msg['from'].bare,mbody=_("Command can't be found."), mtype='groupchat')
		for k in main.R.message_map:
			l = main.R.message_map[k](self.build_msg(msg))
			for res,to in l:
				if not (to == None or res == None):
#					target,mtype=self.get_target(to)
					B.send_message(res,to)
#					self.send_message(mto=target,mbody="%s" % (res),mtype=mtype)
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
				if main.R.has_command(msg['body']) == 1 :
					if(f_ind != -1 and f_ind < 2):
						self.proc_msg(self.build_msg(msg))
#						for res,to in l:
#							if not to == None:
#								target,mtype=self.get_target(to)
#								if not(res == None):
#									self.send_message(mto=target,mbody="%s" % (res),mtype=mtype)
#								else:
#									self.send_message(mto=target,mbody=_("Type /help HELPENTRY to get help. Leave HELPENTRY to empty to get all registered help."),mtype=mtype)
#				else:
#					self.send_message(mto=msg["from"].bare,mbody=_("Command can't be found."),mtype='chat')
				for k in main.R.message_map:
					l = main.R.message_map[k](self.build_msg(msg))
					for res,to in l:
						if not (to == None or res == None):
							#target,mtype=self.get_target(to)
							B.send_message(res,to)
#							self.send_message(mto=target,mbody="%s" % (res),mtype=mtype)

	def proc_msg(self,msg):
		if msg["type"] == 'muc':
			target = msg["mucroom"]
			r_jid = "xmpp:"+self.get_real_jid(msg["from"].split(':')[1])
		else:
			target = msg["from"]
			r_jid = msg["from"]
		if target in lang.lang_map:
			lang.chg_loc(lang.lang_map[target])
		else:
			lang.lang_map[target]=lang.c_locale["default"]
			lang.chg_loc(lang.lang_map[target])
		purecmd = main.R.get_purecmd(msg['body'])
		if privilege.check_priv(purecmd,r_jid):
			main.R.go_call(msg,"xmpp:")
		else:
			B.send_message(_("%(username)s: Insufficient privileges.") % {'username':r_jid}, msg["from"])

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
			return jid

	def build_msg(self,msg):
		r=dict()
		if msg["type"] in ('chat', 'normal'):
			#priv chat
			r["from"] = "xmpp:"+str(msg["from"].bare)
			#remove resource xmpp:xxx@im.aaa.com
			r['type'] = "normal"
		else:
			r["mucroom"] = "xmpp:"+str(msg["from"].bare)
			#xmpp:xxx@conference.im.aaa.com
			r['mucnick'] = str(msg['mucnick'])
			r["from"] = "xmpp:"+str(msg["from"])
			#xmpp:xxx@conference.im.aaa.com/usernick
			r["realfrom"] = "xmpp:"+self.get_real_jid(str(msg["from"]))
			#xmpp:xxx@im.aaa.com
			r['type'] = "muc"
		r['body'] = str(msg["body"])
		return r

	def get_target(self,to):
		target = re.search('xmpp\:(\S*)\/.+',to)
		if target == None:
			target = re.search('xmpp\:(\S*)',to).group(1)
			mtype = 'chat'
		else:
			target = target.group(1)
			mtype = 'groupchat'
		return target,mtype

	def send_msg(self,target,content):
		target,mtype = self.get_target(target)
		self.send_message(mto=target,mbody="%s" % (content),mtype=mtype)
		return True

global xmpp_bot

if "resource" in m_conf:
	xmpp_bot = MUCBot(m_conf["jid"]+'/'+m_conf["resource"], m_conf["password"], m_conf["chatrooms"])
else:
	xmpp_bot = MUCBot(m_conf["jid"], m_conf["password"], m_conf["chatrooms"])

@B.defnew_protocal("dosend","xmpp:")
def xmpp_do_send(msg,to):
	xmpp_bot.send_msg(to,msg)
	return True

if xmpp_bot.connect():
	xmpp_bot.auto_authorize = False
	xmpp_bot.makePresence(pfrom=m_conf["jid"], pstatus='', pshow='')
	xmpp_bot.sendPresence(pto=m_conf["jid"], ptype='probe')
	xmpp_bot.process(block=False)
