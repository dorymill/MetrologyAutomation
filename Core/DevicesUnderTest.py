# DUT Classes and Methods
import pyvisa as pv
import numpy as np
import time
import math
import os
import matplotlib.pyplot as plt
import pandas as pd
from pyvisa.resources import resource
from Core.Standards import *

class Init():

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.dut = rm.open_resource(resource_address)
        self.dut.timeout = 60e3
 
    def command(self,string): # Send and arbitrary command
        self.dut.write(string)

    def query(self,string): # Send an arbitrary query
        return self.dut.query(string)

class AgilentN5181A(Init):

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.dut = rm.open_resource(resource_address)

    def rf_output(self,power,frequency):
        self.dut.write('OUTP:STAT 0')
        self.dut.write(f'FREQ {frequency}')
        self.dut.write(f'POW:AMPL {power} dBm')
        self.dut.write(f'OUTP:STAT 1')
        time.sleep(3)

    def flatness_test(self,inlist):
        df = pd.read_csv(inlist)

        power = [float(p) for p in df['Power']]
        frequency = [float(f) for f in df['Frequency']]

        power = [p for p in power if math.isnan(p) is False]
        frequency = [f for f in frequency if math.isnan(f) is False]

        for p in power:
            for f in frequency:
                self.dut.write('OUTP:STAT 0')
                self.dut.write(f'FREQ {f}')
                self.dut.write(f'POW:AMPL {p} dBm')
                self.dut.write('OUTP:STAT 1')
                
    def silence(self):
        self.dut.write('OUTP:STAT 0')

class HP3325B(Init):

    def command(self,command):
        self.dut.write(command)

    def sine_output(self, level, frequency, unit='VO'): # VO is pp. V is rms
        self.dut.write('FU 1')
        self.dut.write(f'FR{frequency:.1f}HZ')
        self.dut.write(f'AM{level}{unit}')

    def square_output(self, level, frequency, unit='VO'):
        self.dut.write('FU 2')
        self.dut.write(f'FR{frequency:.1f}HZ')
        self.dut.write(f'AM{level}{unit}')

    def triangle_output(self, level, frequency, unit='VO'):
        self.dut.write('FU 3')
        self.dut.write(f'FR{frequency:.1f}HZ')
        self.dut.write(f'AM{level}{unit}')

    def pos_ramp_output(self,level,frequency,unit='VO'):
        self.dut.write('FU 4')
        self.dut.write(f'FR{frequency:.1f}HZ')
        self.dut.write(f'AM{level}{unit}')

    def neg_ramp_output(self,level,frequency,unit='VO'):
        self.dut.write('FU 5')
        self.dut.write(f'FR{frequency:.1f}HZ')
        self.dut.write(f'AM{level}{unit}')

    def dc_offset(self,offset):
        self.dut.write(f'OF{offset}V')

    def dc_offset_only(self,offset):
        self.dut.write('FU 0')
        self.dut.write(f'OF{offset}V')
        self.dut.write(f'OF{offset}V')

    def silence(self):
        self.dut.write('*RST')
        self.dut.write('*RST')

class HP3314A(Init):

    def triangle_output(self, level, frequency, unit='VO'):
        self.dut.write('FU 3')
        self.dut.write(f'FR{frequency:.1f}HZ')
        self.dut.write(f'AP{level}{unit}')

