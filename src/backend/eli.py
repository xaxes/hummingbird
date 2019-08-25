"""Provides translator layer for ELI's digitisers events."""
from __future__ import print_function # Compatibility with python 2 and 3
from backend.event_translator import EventTranslator
import h5py
from os import listdir
from backend.record import Record, add_record
import time

class ELITranslator(object):
    """Creates Hummingbird events from ELI events."""
    def __init__(self, state):
        self.library = "eli"

        if not ('ELI' in state and 'DataSource' in state['ELI']):
            raise ValueError("You need to set the '[ELI][DataSource]'"
                             " in the configuration")

        self._data_source = state['ELI']['DataSource']
        self._sleep_interval = state['ELI']['SleepInterval']
        self._current_file = None
        self._current_file_name = None
        self._current_record = None
        self._current_record_no = 1 # starting from 1 by convention
        pass

    def next_event(self):
        """Returns the next event from the set."""
        self._next_record()

        return EventTranslator(self._current_record, self)

    def event_keys(self, evt):
        """Returns the translated keys available"""
        ks = ['data']
        for k in evt.attrs:
            ks.append(k)
        return ks

    def _next_record(self):
        if self._current_file is None:
            self._next_file()

        if self._current_record is None:
            self._current_record_no = 1
        else:
            self._current_record_no = self._current_record_no+1

        try:
            self._current_record = self._current_file[self._record_from_no(self._current_record_no)]['Data']
        except KeyError:
            self._next_file()
            self._next_record()


    def _record_from_no(self, no):
        return "Record_{}".format(no)

    def _next_file(self):
        file = None
        if self._current_file is None:
            file = self._files()[0]
        else:
            found = False
            for idx, f in enumerate(self._files()):
                if found:
                    file = f
                    break
                if f == self._current_file_name and len(self._files()) != idx+1:
                    found = True
            if not found:
                print("waiting for new data")
                time.sleep(self._sleep_interval)
                self._next_file() # TODO: fix recursion depth

        self._current_file = h5py.File(file, 'r')
        self._current_file_name = file

    def _files(self):
        return ["{}/{}".format(self._data_source, f) for f in listdir(self._data_source)]

    def event_id(self, evt):
        return evt.id.id

    def translate(self, evt, key):
        values = {}

        if key == 'data':
            add_record(values, 'native', 'value', evt.value)
            return values

        found = False
        for event_key in evt.attrs.keys():
            if(event_key == key):
                found = True
                add_record(values, 'native', key, evt.attrs[key])
        if(found):
            return values
        else:
            print('%s not found in event' % (key))