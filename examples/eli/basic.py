"""An example of usage of ELI Beamlines backend."""
from __future__ import print_function # Compatibility with python 2 and 3
import analysis.event
import analysis.beamline
import plotting.line
import time

state = {
    'Facility': 'ELI',
    'ELI':
        {
            'DataSource': '/Users/hhes/eli-datasource',
            'SleepInterval': 10
        }
}

def onEvent(evt):
    analysis.event.printProcessingRate()
    # print("Got event({}): {}".format(evt.event_id(), evt.keys()))
    print(evt['data'].items())
    # print("Data: name: {}, data: {}".format(evt['Data'].name, evt['Data'].data))
    plotting.line.plotHistogram(evt['data']['value'])
    # time.sleep(0.1)