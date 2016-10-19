#!/usr/bin/python3
import math,random
import main
import lang

rand = random.SystemRandom()

R = main.R
@R.add("dice","oncommand")
def go_dice(msg,orgmsg):
	try:
		cmd = msg[1]
	except IndexError:
		return None
	try:
		comment = msg[2:]
	except IndexError:
		comment = ""
	r_comment=""
	for i in comment:
		r_comment = r_comment+i+" "
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
		if(cont>100 or rng>100 or rng < 1):
			return None
		res=[]
		ressum=0
		for i in range(0,cont):
			a = rand.randint(1,rng)
			ressum += a
			res.append(a)
		ressum += addn
		if addn>=0:
			return _("%(comment)s Result: %(dices)s+%(addition)i=%(result)i")%{'comment':r_comment,'dices':res,'addition':addn,'result':ressum}
		elif addn<0:
			return _("%(comment)s Result: %(dices)s%(addition)i=%(result)i")%{'comment':r_comment,'dices':res,'addition':addn,'result':ressum}
	else:
		return None

R.set_help("dicebot",_("""Dice bot usage:
/dice [COUNT]d[LIMIT]|[ADDITION] [DESCRIPTION]
Randomize a sort of dices and add them up.
[COUNT] should be less than 100.
[LIMIT] should be less than 100.
Examples:
/dice 2d6
Result: [1, 2]+0=3
/dice 6d6
Result: [3, 5, 4, 3, 2, 4]+0=21
/dice 6d6|4 Testing
Testing Result: [5, 5, 6, 3, 2, 2]+4=27
/dice 3d20|-5 Checking
Checking Result: [9, 1, 20]-5=25"""))
