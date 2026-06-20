'''
Manages the validation object.
Used by the RiskManager to send validation.
'''

# ? IMPORTS
from models.signal import Signal


# & CLASS INIT
class Validation:
    '''
    Represents a validation object.
    '''

    # * CONSTRUCTOR
    def __init__(self, allowed: bool, reason: str|None, signal: Signal):
        self.allowed = allowed
        self.reason = reason
        self.signal = signal