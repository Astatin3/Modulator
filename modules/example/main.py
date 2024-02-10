mm = None

def test(ac, data):
  mm.sendPopupColor(ac.rawClient, 'test!', 'test!', '#600060', True)
  
def init(moduleMaster):
  global mm
  mm = moduleMaster
  mm.addAuthEventListener('exampleTest', test)

def main():
  pass