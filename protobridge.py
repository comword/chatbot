#!/usr/bin/env /usr/bin/python3
import re
import main

class Protocals():
    def __init__(self):
        self.proto_send_map = dict()

    def defnew_protocal(self,*args):
        def proc(f):
            arg = tuple(args)
            if (arg[0] == "dosend"):
                self.proto_send_map[arg[1]] = f
#            elif (tuple(args)[0] == ""):
#                pass
            return f
        return proc

    def go_route(self,msgs):
        res = list()
        for msg,to in msgs['body']:
            tmp = self.send_message(msg,to)
            if not tmp == True:
                res.append((tmp,msgs["from"]))
        return res

    def send_message(self,msg,to):
        proto = re.search("(.*?\:).*",to).group(1)
        if proto in self.proto_send_map:
            res = self.proto_send_map[proto](msg,to)
            if not res == True:
                return _("An error happened in delivering message %(msg)s to %(rec)s") % {'msg':msg,'rec':to}
            return True
        else:
            return _("Unsupported protocal in delivering message %(msg)s to %(rec)s") % {'msg':msg,'rec':to}

R = main.R

@R.add(_(".*\:\s?\/say\s(\S+)\s((.|\n)*)"),"oncommand")
def cmd_say(msg):
    try:
        target = msg["res"].group(1)
        content = msg["res"].group(2)
    except IndexError:
        return [(None,msg["from"])]
    res = main.B.send_message(content,target)
    if res == True:
        return list()
    else:
        return [(res,msg["from"])]

import privilege
privilege.set_priv("say",0)
