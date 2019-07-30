# -*- coding: utf-8 -*-
import shelve


class Persistent:
    def __init__(self, data_id='default'):
        """This class makes data permanent using object storage with shelve.

        Args:
            data_id (str): Unique identifier for the data to be stored.
        """
        self.__dict__['data_id'] = data_id
        if not self._load():
            self._init()
            self._save()

    def __setattr__(self, name, value):
        """Saves the data on each attribute set."""
        self.__dict__[name] = value
        self._save()

    def _load(self):
        """Loads the data."""
        db = shelve.open('./data/' + str(self.__class__.__name__))
        if str(self.data_id) in db:
            self.__dict__.update(db[self.data_id].__dict__)
            db.close()
            return True
        else:
            db.close()
            return False

    def _save(self):
        """Saves the data."""
        db = shelve.open('./data/' + str(self.__class__.__name__))
        db[self.data_id] = self
        db.close()

    def _init(self):
        """Initializes the object. Replace this on your class with custom method."""
        pass
