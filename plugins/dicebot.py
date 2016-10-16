#!/usr/bin/python3
import math,random
import main

rand = random.SystemRandom()

R = main.R
@R.add("dice","oncommand")
def go_dice(msg,orgmsg):
	try:
		cmd = msg[1]
	except IndexError:
		return None
	try:
		comment = msg[2]
	except IndexError:
		comment = ""
	if (cmd.find('d') == -1):
		return None
	if not(cmd.find('|') == -1):
		try:
			addn = int(cmd.split('|',1)[1])
			dcmd = cmd.split('|',1)[0]
		except ValueError:
			return None
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
		return None

R.set_help("dicebot","""Dice bot usage:
/dice """)
