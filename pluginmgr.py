#!/usr/bin/python3
import sys,os,imp
import config
plugindir=os.getcwd()+"/plugins"
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
	print("Loading plugin: " + filename, description)
	return imp.load_module(mod_name, f, filename, description)

plg_list=config.get_plgconf("loading")
for p in plg_list:
	plgmap[p]=load_plugin(plugindir,p)
