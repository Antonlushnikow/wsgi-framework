import abc
from patterns.decorator import class_debug


class Observer(metaclass=abc.ABCMeta):
   def __init__(self):
       self._subject = None
       self._observer_state = None

   @abc.abstractmethod
   def on_update(self, arg):
       pass


@class_debug
class CourseChangeObserver(Observer):
    def on_update(self):
        print(f'Курс был изменен')


@class_debug
class ObservedSubject:
   def __init__(self):
       self._observers = set()
       self._subject_state = None

   def attach(self, observer):
       observer._subject = self
       self._observers.add(observer)

   def detach(self, observer):
       observer._subject = None
       self._observers.discard(observer)

   def notify(self):
       for observer in self._observers:
           observer.on_update()
