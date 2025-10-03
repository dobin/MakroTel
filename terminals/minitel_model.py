import enum


# Minitel types
TYPE_MINITELS = {
    'b': {
        'name': 'Minitel 1',
        'returnable': False,
        'keyboard': 'ABCD',
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    'c': {
        'name': 'Minitel 1',
        'returnable': False,
        'keyboard': 'Azerty',
        'speed': 1200,
        '80columns': False,
        'characters': False 
    },
    'd': {
        'name': 'Minitel 10',
        'returnable': False,
        'keyboard': 'Azerty',
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    'e': {
        'name': 'Minitel 1 color',
        'returnable': False,
        'keyboard': 'Azerty',
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    'f': {
        'name': 'Minitel 10',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    'g': {
        'name': 'Emulator',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 9600,
        '80columns': True,
        'characters': True
    },
    'j': {
        'name': 'Printer',
        'returnable': False,
        'keyboard': None,
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    'r': {
        'name': 'Minitel 1',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    's': {
        'name': 'Minitel 1 color',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 1200,
        '80columns': False,
        'characters': False 
    },
    't': {
        'name': 'Terminatel 252',
        'returnable': False,
        'keyboard': None,
        'speed': 1200,
        '80columns': False,
        'characters': False
    },
    'u': {
        'name': 'Minitel 1B',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 4800,
        '80columns': True,
        'characters': False
    },
    'v': {
        'name': 'Minitel 2',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 9600,
        '80columns': True,
        'characters': True
    },
    'w': {
        'name': 'Minitel 10B',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 4800,
        '80columns': True,
        'characters': False
    },
    'y': {
        'name': 'Minitel 5',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 9600,
        '80columns': True,
        'characters': True
    },
    'z': {
        'name': 'Minitel 12',
        'returnable': True,
        'keyboard': 'Azerty',
        'speed': 9600,
        '80columns': True,
        'characters': True
    },
}


class MINITEL_CLEAR(enum.Enum):
    WHOLE_SCREEN = 0
    CURSOR_TO_END_OF_LINE = 1
    CURSOR_TO_BOTTOM_OF_SCREEN = 2
    BEGINNING_OF_SCREEN_TO_CURSOR = 3
    BEGINNING_OF_LINE_TO_CURSOR = 4
    LINE = 5
    STATUS_LINE = 6
    WHOLE_SCREEN_AND_STATUS_LINE = 7

# Basic Minitel capabilities
BASIC_CAPABILITIES = {
    'name': 'Unknown Minitel',
    'returnable': False,
    'keyboard': 'ABCD',
    'speed': 1200,
    'manufacturer': 'Unknown',
    '80columns': False,
    'characters': False,
    'version': None
}

# Manufacturer identification codes
MANUFACTURERS = {
    'A': 'Matra',
    'B': 'RTIC',
    'C': 'Telic-Alcatel',
    'D': 'Thomson',
    'E': 'CCS',
    'F': 'Fiet',
    'G': 'Fime',
    'H': 'Unitel',
    'I': 'Option',
    'J': 'Bull',
    'K': 'Télématique',
    'L': 'Desmet'
}
