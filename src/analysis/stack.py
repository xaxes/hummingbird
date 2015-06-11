import collections
import ipc
import numpy
from numpy import abs
import h5py
import time, datetime
from datetime import datetime as DT
import pytz

class Stack:
    def __init__(self,name="stack",maxLen=100,outPeriod=100):
        self._maxLen = maxLen
        self._outPeriod = outPeriod
        self._name = name
        self.clear()
        
    def clear(self):
        self._buffer = None
        self._currentIndex = 0
        n = ipc.mpi.nr_workers()
        if n > 1:
            self._outIndex = float(ipc.mpi.rank) / float(n-1) * (self._outPeriod-1)
        else:
            self._outIndex = 0
        self.last_std    = None
        self.last_mean   = None
        self.last_sum    = None
        self.last_median = None
        self.last_min    = None
        self.last_max    = None
        
    def filled(self):
        return self._currentIndex > self._maxLen
    
    def add(self,data):
        if self._buffer is None:
            s = tuple([self._maxLen] + list(data.shape))
            self._buffer = numpy.zeros(shape=s, dtype=data.dtype)
        self._buffer[self._currentIndex % self._maxLen,:] = data[:]
        self._currentIndex += 1
        
    def _getData(self):
        if self.filled():
            return self._buffer
        else:
            return self._buffer[:self._currentIndex]
        
    def std(self):
        self.last_std = self._getData().std(axis=0)
        return self.last_std
    
    def mean(self):
        self.last_mean = self._getData().mean(axis=0)
        return self.last_mean
    
    def sum(self):
        self.last_sum = self._getData().sum(axis=0)
        return self.last_sum
    
    def median(self):
        self.last_median = numpy.median(self._getData(),axis=0)
        return self.last_median
    
    def min(self):
        self.last_min = self._getData().min(axis=0)
        return self.last_min

    def max(self):
        self.last_max = self._getData().max(axis=0)
        return self.last_max

    def write(self,evt, directory=".", png=False, verbose=True):
        outputs = ["std","mean","sum","median","min","max"]
        # Postpone writing?
        if (self._currentIndex % self._outPeriod) != self._outIndex:
            return
        # Reduce
        for o in outputs:
            exec "self.%s()" % o
        # Timestamp for filename
        try:
            dt64 = evt["eventID"]["Timestamp"].datetime64
        except:
	    dt64 = numpy.datetime64(datetime.datetime.utcnow())
        # Convert to US/Pacific local time
        t_loc = datetime.datetime.now()
        t_utc = datetime.datetime.utcnow()
        delta = t_utc-t_loc
        dt64_loc = dt64 + delta.seconds * 1000000
        try:
            fid = evt["eventID"]["Timestamp"].fiducials
        except:
            fid = 0
        fn = "%s/%s-%s-fid%s-rk%i.h5" % (directory,self._name, str(dt64_loc)[:-5], fid, ipc.mpi.rank)
        # Write to H5
        if verbose:
            print "Writing stack to %s" % fn
        with h5py.File(fn,"w") as f:
            for o in outputs:
                exec "f[\"%s\"] = self.last_%s" % (o,o)
        # Write to PNG
        if png:
            import matplotlib as mpl
            mpl.use('Agg')
            import matplotlib.pyplot as plt
            for o in outputs:
                fig = plt.figure()
                ax = fig.add_subplot(111,title="%s %s (%i)" % (o,self._name,evt.event_id()))
                exec "cax = ax.imshow(%s)" % o
                fn = "%s/%s-%s-%i.png" % (directory,o,self._name, evt.event_id()) 
                fig.colorbar(cax)
                fig.savefig(fn)
                plt.clf()
                
