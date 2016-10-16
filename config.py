#!/usr/bin/python3
import os,yaml
conf_p = os.getcwd()+"/"+"config.yaml"
datamap = {}
if os.path.isfile(conf_p):
	conf = open(conf_p)
	datamap = yaml.safe_load(conf)
	conf.close()
else:
	print("Configure file not found at "+conf_p)

def get_plgconf(mod_name):
	return datamap["plugins"][mod_name]
