#!/usr/bin/env /usr/bin/python3

import main
import lang
import config
m_conf=config.get_plgconf("htmlext")

from flask import Flask, request, send_from_directory, render_template, redirect, make_response

class WebServer:
    def __init__(self,port):
        self.app = Flask(__name__,static_folder='html',template_folder='html/templates')
        self.app.root_path = os.getcwd()
        #logging.config.fileConfig(app.root_path+'logging.conf')
        #logger = logging.getLogger('simple')

    def set_router(self):
        @self.app.route('/')
        def send_1():
            pass
