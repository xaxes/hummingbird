# --------------------------------------------------------------------------------------
# Copyright 2016, Benedikt J. Daurer, Filipe R.N.C. Maia, Max F. Hantke, Carl Nettelblad
# Hummingbird is distributed under the terms of the Simplified BSD License.
# -------------------------------------------------------------------------
import collections
import ipc
import numpy as np
from backend import  ureg
from backend import add_record

def averagePulseEnergy(evt, records, outkey="averagePulseEnergy"):
    """Averages across given pulse energies and adds it to evt["analysis"][outkey].

    Args:
        :evt:      The event variable
        :records:  A dictionary of pulse energy ``Records``

    Kwargs:
        :outkey(str):  Data key of resulting ``Record``, default is 'averagePulseEnergy'

    :Authors:
        Filipe Maia
        Benedikt J. Daurer
    """
    pulseEnergy = []
    for pE in records.values():
        if (pE.unit == ureg.mJ):
            pulseEnergy.append(pE.data)
    if pulseEnergy:
        add_record(evt["analysis"], "analysis", outkey, np.mean(pulseEnergy), ureg.mJ)

def printPulseEnergy(pulseEnergies):
    """Expects a dictionary of pulse energy ``Records`` and prints pulse energies to screen."""
    for k,v in pulseEnergies.iteritems():
        print "%s = %s" % (k, (v.data*v.unit))

def printPhotonEnergy(photonEnergies):
    """Expects a dictionary of photon energy ``Records`` and prints photon energies to screen."""
    for k,v in photonEnergies.iteritems():
        print "%s = %s" % (k, v.data*v.unit)
