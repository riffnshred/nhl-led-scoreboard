import json

class ConfigFile:
  def __init__(self, path, size):
    self.path = path
    self.size = size

    self.load()

  def load(self):
    with open(self.path) as f:
      self.json = json.load(f)

    self.data = JSONData(self.json, self.size)

  def save(self):
      with open(self.path, 'w') as f:
        json.dump(self.json, f)

class JSONData:
  '''The recursive class for building and representing objects with.'''
  def __init__(self, obj, size):
    self.size = size

    for k, v in obj.items():
      if isinstance(v, dict):
        setattr(self, k, JSONData(v, size))
      else:
        setattr(self, k, self.parse_attr(k, v))

  def parse_attr(self, key, value):
    if (isinstance(value, list)):
      if (len(value) == 2):
        return [
          self.parse_attr_value(value[0], self.size[0]),
          self.parse_attr_value(value[1], self.size[1])
        ]

    return self.parse_attr_value(value)

  def parse_attr_value(self, value, dimension = None):
    if (isinstance(value, int)):
      return value
    elif (isinstance(value, str) and value.endswith('%')):
      if (dimension is None):
        return float(value[:-1]) / 100.0
      else:
        return round((float(value[:-1]) / 100.0) * dimension)

    return value
      
  def __copy__(self):
    return JSONData(self.__dict__, self.size)

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
      if (not hasattr(self, k)):
        setattr(self, k, v)
