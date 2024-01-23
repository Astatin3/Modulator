import os
import base64 
import json
from hashlib import sha256
from flask import Flask, render_template, Response
from flask import request, redirect, url_for, make_response

import src.packets as packets
import src.utils as utils

class authUser:
  def __init__(self):
    self.username = None
    self.permGroups = []
    self.sha256passwordhash = None

class authClient:
  def __init__(self):
    self.username = None
    self.session = utils.randID(32)
    self.userData = None

    self.timeout = utils.getUnixTime() + (60 * 60 * 1000)
    self.loginTime = utils.getUnixTime()
    self.lastReauth = utils.getUnixTime()

    self.rawClient = None
  def send(type, data):
    self.rawClient.send(type, data)

class authServer:
  def __init__(self, webserv):
    self.rawServer = None
    self.app = None
    self.clients = []
    self.users = []

    self.webserv = webserv

    self.reloadUsers()
    self.rawServer = webserv.rawServer
    self.initRawServer()

  def login(self, c, data):
    if c.clientid != data['cid']:
      c.send('error', 'invalidLoginRequest')
      return

    if int(data['data']['salt']) > (utils.getUnixTime() + 5000):
      c.send('error', 'invalidLoginRequest')
      return

    logins = json.loads(utils.readFile(utils.getRoot('data/')+'creds.json'))
    isValid = False
    validAcc = None
    for acc in self.users:
      hash = utils.hash(str(acc.username)+str(acc.sha256passwordhash)+str(data['data']['salt']))
      if hash == str(data['data']['data']):
        isValid = True
        validAcc = acc
        break

    if isValid:
      if utils.getatribinarr(self.clients, 'rawClient', c):
        c.send('error', 'prelogin')
        return

      ac = authClient()
      ac.username = validAcc.username
      ac.userData = validAcc
      ac.rawClient = c

      self.clients.append(ac)

      c.send('loginSuccess', {
        'username': ac.username,
        'session': ac.session,
        'redir': f'/{self.webserv.defaultTab}/{self.webserv.defaultPage}',
        'timeout': ac.timeout
      })

      return
    else:
      c.send('error', 'invalidLogin')
      return

  def validAc(self, ac):
    if ac == None:
      return False
    if ac.rawClient.address != request.remote_addr:
      return False
    if utils.getUnixTime() > ac.timeout:
      return False

    return True

  def reauth(self, c, data):
    session = data['data']['session']

    ac = utils.getatribinarr(self.clients, 'session', session)

    if not self.validAc(ac):
      c.send('error', 'invalidLoginRequest')
      return

    ac.rawClient = c
    ac.lastReauth = utils.getUnixTime()

    c.send('reauth', {
      'username': ac.username
    })

  def cookieLogin(self, request):
    session = request.cookies.get('session')
    if session == None:
      return None
      
    ac = utils.getatribinarr(self.clients, 'session', session)
    
    return self.validAc(ac)


  def initRawServer(self):
    self.rawServer.addEventListener('login', self.login)
    self.rawServer.addEventListener('reauth', self.reauth)

  def reloadUsers(self):
    data = json.loads(utils.readFile(utils.getRoot('data/')+'creds.json'))

    self.users = []

    for acc in data:
      user = authUser()
      user.username = acc['username']
      user.sha256passwordhash = acc['sha256passwordhash']
      user.permGroups = acc['permGroups']
      self.users.append(user)