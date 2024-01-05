import os
import src.utils as utils
import multiprocessing as mupr

from flask import Flask, render_template, Response
from flask import request, redirect, url_for, make_response

import src.jsonpack as jsonpack
import src.auth as auth

webroot = utils.getRoot('html/')

app = Flask(__name__,
  static_url_path=webroot,
  static_folder=webroot,
  template_folder=webroot)

class webtab():
  def __init__(self):
    self.name = None
    self.pages = []
    self.defaultPage = ''
    self.html = ''

  def recursiveAdder(self, objs):
    html = ''
    for obj in objs:
      if isinstance(obj, webpagefolder):
        html += '<details><summary>' +\
        obj.name +\
        '</summary><ul>\n' +\
        self.recursiveAdder(obj.pages) +\
        '</ul></details>\n'
      else:
        html += f'<li onclick=\'window.location="/{self.name}/{obj.name}"\'>' +\
        obj.name +\
        '</li>\n'
    return html

  def addHtml(self):
    self.html = self.recursiveAdder(self.pages)

  def addPage(self, page):
    self.pages.append(page)
    
class webpagefolder():
  def __init__(self):
    self.name = None
    self.pages = []

class webpage():
  def __init__(self):
    self.name = None
    self.location = None

@app.route('/')
def index():
  isValid = app.authServer.cookieLogin(request)
  if not isValid:
    return redirect("/login", code=302)
  else:
    return redirect(f'/{app.defaultTab}/{app.defaultPage}', code=302)

@app.route('/login')
def loginPage():
  isValid = app.authServer.cookieLogin(request)
  if isValid:
    return redirect(f'/{app.defaultTab}/{app.defaultPage}', code=302)

  return make_response(open(f'{webroot}nav.html', 'r').read()
    .replace('<!--Place body here!!!-->', open(f'{webroot}login.html', 'r').read())
    .replace('<!--Place tabs here!!!-->', '<a href="/login" role="button" class="outline topnav-button text-white">Login</a>')
    .replace('<!--Place title here!!!-->', app.title)
    .replace('<!--Place defaultPage here!!!-->', '/login'))

def recursivePageLocationFinder(pagename, objs):
  returnVal = None
  for obj in objs:
    if isinstance(obj, webpagefolder):
      tmp = recursivePageLocationFinder(pagename, obj.pages)
      if tmp != None:
        returnVal = tmp
    else:
      if obj.name == pagename:
        returnVal = obj.location
  return returnVal

@app.route('/<tabname>/<pagename>')
def page(tabname, pagename):
  
  isValid = app.authServer.cookieLogin(request)
  if not isValid:
    return redirect("/login", code=302)
  
  try:
  
    tab = utils.getatribinarr(app.webtabs, 'name', tabname)
    pageloc = recursivePageLocationFinder(pagename, tab.pages)

    return make_response(open(utils.getRoot('html/nav.html'), 'r').read()
      .replace('<!--Place body here!!!-->', open(utils.getRoot(pageloc), 'r').read())
      .replace('<!--Place tabs here!!!-->', app.tabHtml)
      .replace('<!--Place pages here!!!-->', tab.html)
      .replace('<!--Place title here!!!-->', app.title)
      .replace('<!--Place defaultPage here!!!-->', f'/{app.defaultTab}/{app.defaultPage}'))
  except:
    return redirect("/login", code=302)

@app.route('/src/<file>')
def src(file):
  return app.send_static_file(f'src/{file}')

@app.errorhandler(404)
def err404(err):
  return redirect("/", code=302)

class webserv():
  def __init__(self):
    self.title = 'Modulator'
    self.port = 443
    self.host = '0.0.0.0'
    self.verbose = False
    self.secure = True
    self.tabHtml = ''
    self.webtabs = []
    self.defaultTab = 'main'
    self.defaultPage = ''

    self.app = None

  def start(self):
    if not self.verbose:
      import logging
      log = logging.getLogger('werkzeug')
      log.setLevel(logging.ERROR)

    if self.secure:
      dataroot = utils.getRoot("data/")
      sslcontext = (f'{dataroot}selfsign.crt', f'{dataroot}selfsign.key')
    else:
      sslcontext = None

    self.proc = mupr.Process(target=app.run, kwargs=dict(debug=self.verbose, port=self.port, host=self.host, ssl_context=sslcontext))

    def tabHtml(path, name):
      return f'<a href="{path}" role="button" class="outline topnav-button text-white">{name}</a>'

    for tab in self.webtabs:
      self.tabHtml += tabHtml(f'/{tab.name}/{tab.defaultPage}', tab.name)
      if tab.name == self.defaultTab:
        self.defaultPage = tab.defaultPage

    app.authServer = auth.startAuthListener(app)

    app.defaultTab = self.defaultTab
    app.defaultPage = self.defaultPage
    app.webtabs = self.webtabs
    app.tabHtml = self.tabHtml

    app.title = self.title
    self.app = app
    self.proc.start()

  def stop(self):
    self.proc.terminate()
  
  # def sendfatal(self, err):
  #   self.rawServer.broadcast(jsonpack.pack({
  #       'type': 'error',
  #       'severity': 'fatal',
  #       'error': err
  #     }))