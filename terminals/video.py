

from abc import abstractmethod


class VideoTerminal():
    def __init__(self, terminal):
        self.terminal = terminal

    @abstractmethod
    def color(self, character = None, background = None):
        pass

    @abstractmethod
    def position(self, column, row, relative = False):
        pass

    @abstractmethod
    def effect(self, underline = None, blinking = None, inversion = None):
        pass

    @abstractmethod
    def cursor(self, visible):
        pass

    @abstractmethod
    def echo(self, active):
        pass
    
    @abstractmethod
    def clear(self, scope = 'all'):
        pass

    # only minitel?!
    def size(self, width = 1, height = 1):
        pass

    @abstractmethod
    def repeat(self, character, length):
        pass

    @abstractmethod
    def beep(self):
        pass

    @abstractmethod
    def line_start(self):
        pass

    @abstractmethod
    def delete(self, nb_column = None, nb_row = None):
        pass

    @abstractmethod
    def insert(self, nb_column = None, nb_row = None):
        pass

