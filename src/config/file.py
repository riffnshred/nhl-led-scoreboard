import json

class ConfigFile:
  def __init__(self, path, size=None):
    self.path = path
    self.size = size

    self.load()

  def load(self):
    try:
      with open(self.path) as f:
        self.json = json.load(f)

      self.data = JSONData(self.json, self.size)
    except:
      print('Config file {} not found!'.format(self.path))

  def save(self):
    with open(self.path, 'w') as f:
      json.dump(self.json, f)

  def combine(self, file):
    if (hasattr(self, 'data') and hasattr(file, 'data')):
      self.data.__merge_nested__(file.data)

class JSONData:
  '''The recursive class for building and representing objects with.'''
  def __init__(self, obj, size):
    if (size is not None):
      self.size = size

    for k, v in obj.items():
      if isinstance(v, dict):
        setattr(self, k, JSONData(v, size))
      else:
        setattr(self, k, self.parse_attr(k, v))

  def parse_attr(self, key, value):
    if (isinstance(value, list)):
      if (len(value) == 2):
        return (
          self.parse_attr_value(value[0], self.size[0]),
          self.parse_attr_value(value[1], self.size[1])
        )
      else:
        return tuple(map(lambda x: self.parse_attr_value(x), value))

    return self.parse_attr_value(value)

  def parse_attr_value(self, value, dimension = None):
    if (isinstance(value, int)):
      return value
    elif (isinstance(value, str) and value.endswith('%')):
      if (dimension is None):
        # Convert to percent (0 - 1)
        return float(value[:-1]) / 100.0
      else:
        # Convert to pixels taking into account dimension (width or height)
        return round((float(value[:-1]) / 100.0) * (dimension - 1))
    elif (isinstance(value, list)):
      return sum([self.parse_attr_value(x, dimension) for x in value])

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

  def __merge__(self, obj, overwrite=False):
    for k, v in obj:
      if (overwrite or not hasattr(self, k)):
        setattr(self, k, v)

  def __merge_nested__(self, obj, overwrite=False):
    for k, v in obj:
      if (isinstance(v, JSONData)):
        if (hasattr(self, k)):
          getattr(self, k).__merge_nested__(v)
        else:
          setattr(self, k, v.__copy__())
      else:
        setattr(self, k, v)
