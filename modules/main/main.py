mm = None

def logout(ac, data):
  ac.send('redir', {
    "location": "/"
  })
  mm.authServer.unauth(ac)

def loadSessions(ac):
  obj = []
  for client in mm.authServer.clients:
    if client.user != ac.user:
      continue
    obj.append({
      'username': client.username,
      'address': client.rawClient.address,
      'currentPage': client.currentPage,
      'clientid': client.rawClient.clientid,
      'timeout': client.timeout
    })
    # obj.append(client.session)
  ac.send('sessions', obj)

def unauth(ac, data):
  removeClient = mm.getAuthClientByID(data['data'])
  if removeClient == None:
    return
  if removeClient.user == ac.user:
    removeClient.send('redir', {
      "location": "/"
    })
    mm.unauth(removeClient)
    loadSessions(ac)

def init(moduleMaster):
  global mm
  mm = moduleMaster
  mm.addAuthEventListener('logout', logout)
  mm.addAuthEventListener('unauth', unauth)
  mm.addPageEventListener('/main/User', loadSessions)

def main():
  pass