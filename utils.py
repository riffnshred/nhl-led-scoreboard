import os
import debug

def get_file(path):
  dir = os.path.dirname(__file__)
  return os.path.join(dir, path)