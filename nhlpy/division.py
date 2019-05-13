import requests

from .constants import BASE_URL


class Division:
    """This class maps to the division endpoint of the NHL's API.

    Provides information about the divisions in the NHL. The class does
    not take in any parameters when instantiated. After it is instantiated
    it does have two instance variables ``id`` and ``data``

    Usage::
    >>> from nhlpy import division
    >>> d = division.Division()
    >>> d.info(8)
    >>> d.all()
    """

    def __init__(self):
        self.id = None
        self.data = None

    def all(self):
        """ All available information from all available divisions.

        :returns: information about all divisions
        :rtype: dictionary
        """
        response = requests.get("{0}/divisions".format(BASE_URL))
        self.data = response.json()
        del self.data["copyright"]

        return self.data

    def info(self, id):
        """Information from a specific division.
        The only valid division ID's are 1-18. If you try to use
        an int greater than 18, or 0 or less, then an exception
        will be raised.

        :param id: The ID of the division (only valid integers are 1-18)
        :type id: int
        :returns: information about that specific division
        :rtype: dictionary
        """
        self.id = id

        if self.id == 0:
            raise Exception("The division ID cannot be 0")

        if self.id < 0:
            raise Exception("The division ID cannot be a negative int")

        if self.id > 18:
            raise Exception("The division ID cannot be an int greater than 18")

        response = requests.get("{0}/divisions/{1}".format(BASE_URL, self.id))
        self.data = response.json()
        del self.data["copyright"]

        return self.data
