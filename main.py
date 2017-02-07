#!/usr/bin/env /usr/bin/python3
import sys,os,imp,time
sys.path.append(".")
import lang
import config
import register
R = register.R()
import privilege
import database

if __name__ == "__main__":
	import pluginmgr
	import logging
	logging.basicConfig(level=logging.INFO,
		                    format='%(levelname)-8s %(message)s')
	while True:
		time.sleep(1)
