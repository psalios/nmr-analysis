class Observer:

    def __init__(self, logger):
        self.logger = logger
        self._observers = []

    def addObserver(self, observer):
        self._observers.append(observer)

    def notifyObservers(self, *arg):
        for observer in self._observers:
            observer(*arg)
