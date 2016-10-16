#!/usr/bin/python3
import math,random
import xmpp
import logging

rand = random.SystemRandom()
@xmpp.register("dice")
def go_dice(msg,orgmsg):
	cmd = msg[1]
	try:
		comment = msg[2]
	except IndexError:
		comment = ""
	if (cmd.find('d') == -1):
		return "Example: 2d20|+5"
	if not(cmd.find('|') == -1):
		try:
			addn = int(cmd.split('|',1)[1])
			dcmd = cmd.split('|',1)[0]
		except ValueError:
			return "Example: 2d20|+5"
	else:
		addn = 0
		dcmd = cmd
	if(dcmd.split('d',1)[0].isdigit() and dcmd.split('d',1)[1].isdigit()):
		cont = int(dcmd.split('d',1)[0])
		rng = int(dcmd.split('d',1)[1])
		res=[]
		ressum=0
		for i in range(0,cont):
			a = rand.randint(1,rng)
			ressum += a
			res.append(a)
		ressum += addn
		if addn>=0:
			return("%s Result: %s+%i=%i"%(comment,res,addn,ressum))
		elif addn<0:
			return("%s Result: %s%i=%i"%(comment,res,addn,ressum))
	else:
		return "Example: 2d20|+5"
	
