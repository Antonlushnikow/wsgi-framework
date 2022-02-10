import abc
from patterns.decorator import class_debug


class Observer(metaclass=abc.ABCMeta):
    def __init__(self):
        self._subject = None

    @abc.abstractmethod
    def on_update(self, *args):
        pass


@class_debug
class ObservableSubject:
   def __init__(self):
       self._observers = set()
       self._subject_name = None

   def attach(self, observer):
       observer._subject = self
       self._observers.add(observer)

   def detach(self, observer):
       observer._subject = None
       self._observers.discard(observer)

   def notify(self):
       for observer in self._observers:
           observer.on_update(self._subject_name)
