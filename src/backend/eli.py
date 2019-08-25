"""Provides translator layer for ELI's digitisers events."""
from __future__ import print_function # Compatibility with python 2 and 3
from backend.event_translator import EventTranslator

class ELITranslator(object):
    def __init__(self, state):
        self.library = "eli"
        pass

    def next_event(self):
        """Returns the next event from the set."""
        return EventTranslator({}, self)

    def event_keys(self, _):
        """Returns the translated keys available"""
        return []