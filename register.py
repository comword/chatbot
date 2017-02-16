#!/usr/bin/env /usr/bin/python3
import lang
import re
import main

class R():
	def __init__(self):
		self.cmd_list = list()
		self.command_map={}
		self.message_map={}
		self.help_map={}
		self.cmd_alias={}
		self.command_map[_(".*\:\s?\/help\s?(\S+)?\s?")] = self.show_help
	def add(self,*args):
		def decorator(f):
			arg = tuple(args)
			if(arg[1] == "oncommand"):
				self.command_map[arg[0]] = f
				self.cmd_list.append(self.get_purecmd_regx(arg[0]))
			elif(arg[1] == "onmessage"):
				self.message_map[arg[0]] = f
			return f
		return decorator

	def show_help(msg):
		try:
			cmd = msg["res"].group(1)
		except IndexError:#Show all help entry
			#return _("Type /help HELPENTRY to get help. Leave HELPENTRY to empty to get all registered help.")
			res = "All help:\n"
			for i in self.help_map:
				res += (i+'\n')
			return res,msg["from"]
		if cmd in self.help_map:
			return self.help_map[cmd],msg["from"]
		else:
			return [(_("The help %(name)s is not being registered in manual.") % {'name':cmd},msg["from"])]

	def set_help(self,command,context):
		self.help_map[command] = context

	def set_alias(self,command,alias):
		self.cmd_alias[alias] = command

	def go_call(self,command,protocal):
		command['body'] = protocal + command['body'] #xmpp:/xxx
		for cmd in self.cmd_alias:
			try:
				res = re.search(cmd,command['body'])
			except:
				return main.B.send_message(_("Command %(cmd_userinput)s caused a error in %(cmd). It's a bug.") % {'cmd_userinput': command['body'], 'cmd': cmd},command["from"])
			if res != None:
				real_cmd = self.cmd_alias[cmd]
				if real_cmd in self.command_map:
					command["res"] = res
					func_res = self.command_map[real_cmd](command)
					send_result = main.B.go_route(self.build_route_msg(func_res,command["from"]))
					for msg,to in send_result:
						return main.B.send_message(msg,to)
					return True
				else:
					return main.B.send_message(_("Command %s found in alias name, but it's a broken alias link. It's a bug.") % cmd,command["from"])
		for cmd in self.command_map:
			res = re.search(cmd,command['body'])
			if res != None:
				command["res"] = res
				func_res = self.command_map[cmd](command)
				send_result = main.B.go_route(self.build_route_msg(func_res,command["from"]))
				for msg,to in send_result:
					return main.B.send_message(msg,to)
				return True
		return main.B.send_message(_("Command %s can't be executed.") % command['body'],command["from"])

	def get_purecmd(self,cmd):
		tmp = re.search('\/(\w+)', cmd)
		if tmp != None:
			return tmp.group(1)

	def get_purecmd_regx(self,cmd):
		tmp = re.search('\\\/(\w+)', cmd)
		if tmp != None:
			return tmp.group(1)

	def refresh_command_map_lang(self):
		tmp={}
		cmd_list = list()
		for k in self.command_map:
			if not _(k) == k:
				tmp[_(k)] = k
				cmd_list.append(self.get_purecmd_regx(_(k)))
			cmd_list.append(self.get_purecmd_regx(k))
		self.cmd_alias = tmp
		self.cmd_list = cmd_list

	def has_command(self, cmd):
		if self.get_purecmd(cmd) in self.cmd_list:
			return 1
		else:
			return 0

	def build_route_msg(self,msgs,rfrom):
		res = dict()
		res["body"] = msgs
		res["from"] = rfrom
		return res
