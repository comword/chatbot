#!/usr/bin/env /usr/bin/python3

import main
import lang
import config
import database
m_conf=config.get_plgconf("htmlext")

import os
import threading
from flask import Flask, request, send_from_directory, render_template, redirect, make_response

def m_valid_login(user,passw):
#	if user in pluginmgr.plgmap["xmpp"].m_bot.muc_jid:
#		print(_("Redirecting user privilege change to real JID."))
#		user = pluginmgr.plgmap["xmpp"].m_bot.muc_jid[user]
	ud = database.get_user_details(user)
	if ud == None:
		return False
	return True

class WebServer:
	def __init__(self):
		self.app = Flask(__name__,static_folder=m_conf["base"],template_folder=m_conf["base"]+'/templates')
		self.app.root_path = os.getcwd()
		self.set_router()
	def set_router(self):
		@self.app.route('/')
		def send_1():
			user = request.cookies.get('username')
			if (user == None):
				return redirect("login.html")
			return redirect("home.html")
		@self.app.route('/login.html')
		def send_2():
			user = request.cookies.get('username')
			if (user == None):
				return send_from_directory(self.app.static_folder, 'login.html')
			return redirect("home.html")
		@self.app.route('/login_action.cgi',methods=['POST', 'GET'])
		def send_3():
			error = None
			if request.method == 'POST':
				user = request.form['inputUsername']
				if (m_valid_login(user,None) == True):
#                    privilege = dbman.get_privilege(user);
#                    client_jwt = myjwt.generate_JWT(user,privilege)
					response = make_response('home.html')
					response.set_cookie('username', user)
					return response
				return _("Wrong username.")
			return 'Bad Request', 400, {'Content-Type': 'text/html'}#Generate http 400
		@self.app.route('/<path:filename>')
		def send_4(filename):
			return send_from_directory(self.app.static_folder, filename)
		@self.app.route('/js/<path:filename>')
		def send_5(filename):
			return send_from_directory(self.app.static_folder+'/js', filename)
		@self.app.route('/css/<path:filename>')
		def send_6(filename):
			return send_from_directory(self.app.static_folder+'/css', filename)
		@self.app.route('/fonts/<path:filename>')
		def send_7(filename):
			return send_from_directory(self.app.static_folder+'/fonts', filename)
def st():
	web = WebServer()
#	web.app.run(host="0.0.0.0",port=m_conf["listen"],debug=True,threaded=True)
	web.app.run(host="0.0.0.0",port=m_conf["listen"],threaded=True)

threading.Thread(target = st, args = (), name = 'thread-htmlext').start()
