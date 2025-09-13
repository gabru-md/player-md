from abc import abstractmethod

from lib.log import Logger


class Generator:

    def __init__(self, config):
        self.config = config
        self.log = Logger.get_log(self.__class__.__name__)

    @abstractmethod
    def generate(self, bar, key, *args):
        pass
