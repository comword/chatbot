class R():
	def __init__(self):
		self.command_map={}
		self.message_map={}
		self.help_map={}

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
			return ("Command %s is not being registered in manual.")

	def set_help(self,command,context):
		self.help_map[command] = context
