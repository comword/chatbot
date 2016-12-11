#!/usr/bin/env /usr/bin/python3
import lang
class R():
	def __init__(self):
		self.command_map={}
		self.message_map={}
		self.help_map={}
		self.cmd_alias={}
	def add(self,*args):
		def decorator(f):
			f.register = tuple(args)
			if(tuple(args)[1] == "oncommand"):
				self.command_map[tuple(args)[0]] = f
			elif(tuple(args)[1] == "onmessage"):
				self.message_map[tuple(args)[0]] = f
			return f
		return decorator

	def get_map(self):
		return self.command_map

	def get_help(self,command):
		if command in self.help_map:
			return self.help_map[command]
		else:
			return _("The help of plugin %(pluginname)s is not being registered in manual.") % {'pluginname':command}

	def set_help(self,command,context):
		self.help_map[command] = context

	def set_alias(self,command,alias):
		self.cmd_alias[alias]=command

	def get_command(self,cmd):
		if cmd in self.cmd_alias:
			if self.cmd_alias[cmd]==cmd:
				return _("Command %s has bad alias name.") + _("Type /help (plugin) to get help. Type /listplugins to list all plugins.") % cmd
			elif self.cmd_alias[cmd] in self.command_map:
				return self.command_map[self.cmd_alias[cmd]]
			else:
				return _("Command with alias name %s can't be found.") + _("Type /help (plugin) to get help. Type /listplugins to list all plugins.") % cmd
		elif cmd in self.command_map:
			return self.command_map[cmd]
		else:
			return _("Command %s can't be found.") % cmd

	def refresh_command_map_lang(self):
		tmp={}
		for k in self.command_map:
			if not _(k)==k:
				tmp[_(k)]=k
		self.cmd_alias = tmp

	def has_command(self, cmd):
		if cmd in self.cmd_alias:
			if self.cmd_alias[cmd]==cmd:
				return -1
			elif self.cmd_alias[cmd] in self.command_map:
				return 1
			else:
				return 0
		elif cmd in self.command_map:
			return 1
		else:
			return 0
