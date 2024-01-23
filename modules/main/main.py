from modules.main import test as test

mm = None

def test1(ac, data):
  mm.sendPopupColor(ac.rawClient, 'test!', 'test!', '#600060', True)

def init(moduleMaster):
  global mm
  mm = moduleMaster
  mm.addAuthEventListener('test1', test1)

def main():
  pass