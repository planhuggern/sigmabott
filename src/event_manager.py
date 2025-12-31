class EventManager:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def unsubscribe(self, observer):
        self._observers.remove(observer)

    def notify(self, event, data=None):
        for observer in self._observers:
            observer.update(event, data)


class Observer:
    def update(self, event, data):
        pass
