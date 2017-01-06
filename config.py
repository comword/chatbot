#!/usr/bin/env /usr/bin/python3
import os,yaml

datamap = {}
conf_p = os.getcwd()+"/"+"config.yaml"

if os.path.isfile(conf_p):
	conf = open(conf_p)
	datamap = yaml.safe_load(conf)
	conf.close()
else:
	print(("Configure file not found at %s") % conf_p )
	exit(0)
	
def get_plgconf(mod_name):
	return datamap["plugins"][mod_name]
