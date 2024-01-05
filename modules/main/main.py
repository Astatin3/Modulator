from modules.main import test as test

def test1(ac, data):
  print(ac)
  print(data)

def main(mm):
  # mm.addAuthEventListener('test1', test1)
  print(mm.rawServer.addEventListener('test1', test1))
  #mm.rawServer.addEventListener('login', test1)