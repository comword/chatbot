#!/usr/bin/python3
import sys,os,imp,time
sys.path.append(".")
import config
import pluginmgr
import logging

logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
xmpp = pluginmgr.plgmap["xmpp"].start_xmpp()
xmpp.process(block=False)
while True:
	time.sleep(1)
