#!/usr/bin/env /usr/bin/python3
import math,random
import main
import lang

rand = random.SystemRandom()

R = main.R
@R.add(_("\/dice\s(\d+)d(\d+)\|?([+|-]?\d+)?\s?(.*)\s?"),"oncommand")
def go_dice(msg):
	try:
		cont = int(msg["res"].group(1))
		rng = int(msg["res"].group(2))
	except:
		return None,msg["from"]
	try:
		add = int(msg["res"].group(3))
	except:
		add = 0
	try:
		comment = msg["res"].group(4)
	except IndexError:
		comment = ""
	if(cont>100 or rng>1000 or rng < 1):
		return None,msg["from"]
	res=[]
	ressum=0
	for i in range(0,cont):
		a = rand.randint(1,rng)
		ressum += a
		res.append(a)
	ressum += add
	if add>=0:
		return [(_("%(comment)s Result: %(dices)s+%(addition)i=%(result)i")%{'comment':comment,'dices':res,'addition':add,'result':ressum},msg["from"])]
	elif add<0:
		return [(_("%(comment)s Result: %(dices)s%(addition)i=%(result)i")%{'comment':comment,'dices':res,'addition':add,'result':ressum},msg["from"])]

@R.add(_("\/privdice\s(\d+)d(\d+)\|?([+|-]?\d+)?\s?(.*)\s?"),"oncommand")
def go_privdice(msg):
	try:
		cont = int(msg["res"].group(1))
		rng = int(msg["res"].group(2))
	except:
		return None,msg["from"]
	try:
		add = int(msg["res"].group(3))
	except:
		add = 0
	try:
		comment = msg["res"].group(4)
	except IndexError:
		comment = ""
	if(cont>100 or rng>1000 or rng < 1):
		return None,msg["from"]
	res=[]
	ressum=0
	for i in range(0,cont):
		a = rand.randint(1,rng)
		ressum += a
		res.append(a)
	ressum += add
	if add>=0:
		return [(_("%(comment)s Result: %(dices)s+%(addition)i=%(result)i")%{'comment':comment,'dices':res,'addition':add,'result':ressum},msg["realfrom"]),
		(_("Result sent."),msg["from"])]
	elif add<0:
		return [(_("%(comment)s Result: %(dices)s%(addition)i=%(result)i")%{'comment':comment,'dices':res,'addition':add,'result':ressum},msg["realfrom"]),
		(_("Result sent."),msg["from"])]

R.set_help("dicebot",_("""Dice bot usage:
/dice [COUNT]d[LIMIT]|[ADDITION] [DESCRIPTION]
Randomize a sort of dices and add them up.
[COUNT] should be less than 100.
[LIMIT] should be less than 1000.
Examples:
/dice 2d6
Result: [1, 2]+0=3
/dice 6d6
Result: [3, 5, 4, 3, 2, 4]+0=21
/dice 6d6|4 Testing
Testing Result: [5, 5, 6, 3, 2, 2]+4=27
/dice 3d20|-5 Checking
Checking Result: [9, 1, 20]-5=25"""))
