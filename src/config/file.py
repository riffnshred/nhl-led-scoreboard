import json

class ConfigFile:
  def __init__(self, path):
    self.path = path
    self.load()

  def load(self):
    with open(self.path) as f:
      self.json = json.load(f)

    self.data = JSONData(self.json)

  def save(self):
      with open(self.path, 'w') as f:
        json.dump(self.json, f)

class JSONData:
  '''The recursive class for building and representing objects with.'''
  def __init__(self, obj):
    for k, v in obj.items():
      if isinstance(v, dict):
        setattr(self, k, JSONData(v))
      else:
        setattr(self, k, v)

  def __copy__(self):
    return JSONData(self.__dict__)

  def __contains__(self, item):
    return item in self.__dict__

  def __getitem__(self, val):
    return self.__dict__[val]

  def __iter__(self):
      for attr, value in self.__dict__.items():
          yield attr, value

  def __repr__(self):
    return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for
      (k, v) in self.__dict__.items()))

  def __merge__(self, obj):
    for k, v in obj:
      if (hasattr(self, k)):
        setattr(self, k, v)
