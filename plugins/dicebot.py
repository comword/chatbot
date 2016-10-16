#!/usr/bin/python3
import math,random
import xmpp
import logging

rand = random.SystemRandom()
@xmpp.register("dice")
def go_dice(msg):
	com = msg['body']
	xmpp.m_bot.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mucnick'],
                              mtype='groupchat')
