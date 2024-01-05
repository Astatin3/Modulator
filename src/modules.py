import json
import importlib
import sys

import src.web as web
import src.utils as utils

class module():
  def __init__(self):
    self.name = None
    self.module = None
    self.rootdir = None
    self.tabs = []

  def initSelf(self):
    spec = importlib.util.spec_from_file_location(self.name, utils.getRoot(self.entrypoint))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    self.module = module
  
  def run(self, moduleMaster):
    self.module.main(moduleMaster)

class moduleMaster():
  def __init__(self):
    self.modules = []
    self.webserv = None
    
    self.app = None
    self.rawServer = None
    self.authServer = None

  def initModules(self, webserv):
    self.webserv = webserv

    mdirs = utils.listSubdirs(utils.getRoot('modules/'))

    for mname in mdirs:
      mjson = json.loads(open(utils.getRoot(f'modules/{mname}/module.json')).read())
      m = module()
      m.name = mjson['name']
      m.entrypoint = mjson['entrypoint']
      
      for tab in mjson['tabs']:
        mtab = utils.getatribinarr(self.webserv.webtabs, 'name', tab['name'])

        if mtab == None:
          mtab = web.webtab()
          mtab.name = tab['name']
          m.tabs.append(mtab)

        def recursiveAdder(objs):
          tmpPages = []
          for obj in objs:
            if obj['type'] == 'folder':
              folder = web.webpagefolder()
              folder.name = obj['name']
              tmpTmpPages = recursiveAdder(obj['pages'])
              for tmpobj in tmpTmpPages:
                folder.pages.append(tmpobj)
              tmpPages.append(folder)
            else:
              mpage = web.webpage()
              mpage.name = obj['name']
              mpage.location = obj['location']
              tmpPages.append(mpage)
          return tmpPages

        tmpPages = recursiveAdder(tab['pages'])

        for obj in tmpPages:
          mtab.pages.append(obj)

        mtab.defaultPage = tab['defaultPage']

        self.webserv.webtabs.append(mtab)

      m.initSelf()
      self.modules.append(m)

    for tab in webserv.webtabs:
      tab.addHtml()

  def runModules(self):
    self.app = self.webserv.app
    self.rawServer = self.app.rawServer
    self.authServer = self.app.authServer

    for module in self.modules:
      module.run(self)
  
  def getRawClients(self):
    return self.rawServer.clients
  
  def addRawEventListener(self, eventName, func):
    self.rawServer.addEventListener(eventName, func)
  
  def getAuthClients(self):
    return self.authServer.clients
  
  def addAuthEventListener(self, eventName, func):
    def tmpfunc(self, c, data):
      if not c in self.rawServer.clients:
        return
      ac = utils.getatribinarr(self.authServer.clients, 'rawClient', c)
      if ac == None:
        return

      func(ac, data)

    self.rawServer.addEventListener(eventName, tmpfunc)