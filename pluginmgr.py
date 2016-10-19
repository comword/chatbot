#!/usr/bin/python3
import sys,os,imp
import config
import main
import lang

R = main.R
plugindir=os.getcwd()+config.get_plgconf("path")
sys.path.append(plugindir)
plgmap={}

def list_plugins():
	tmpl=[]
	for parent,dirnames,filenames in os.walk(plugindir):
		for f in filenames:
			ext = f[f.index("."):]
			if(ext == ".py" or ext == ".so" or ext == ".pyc"):
				tmpl.append(f)
		return tmpl

def load_plugin(plugindir,mod_name):
	f, filename, description = imp.find_module(mod_name,[plugindir])
	print(_("Loading plugin: %(name)s , %(desc)s") %{'name':filename, 'desc':description})
	return imp.load_module(mod_name, f, filename, description)

@R.add("listplugins","oncommand")
def list_plugin(msg,orgmsg):
	res = _("All plugin:\n")
	for k in plgmap:
		res+=k
		res+="\n"
	return res

plg_list=config.get_plgconf("loading")
for p in plg_list:
	plgmap[p]=load_plugin(plugindir,p)
