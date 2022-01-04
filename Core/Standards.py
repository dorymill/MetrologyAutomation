from collections import abc
import pyvisa as pv
import numpy as np
import time, math, os, re
import matplotlib.pyplot as plt
import pandas as pd

# Utilize the builtin help method and attribute definitions to build in an interactive API loop
# and have it called when this script is ran directly

# Standard Functions

def initialize_std(name='standard'): # Initialize a standard instrument
    clear()
    rmq = pv.ResourceManager()
    instruments = [dev for dev in rmq.list_resources()]

    print('\nAvailable devices:\n')

    for i,dev in enumerate(instruments):
        print(f'{i} ) {dev}')

    index1 = int(input(f"\nEnter the {name}'s index | "))
    clear()

    return instruments[index1]

def initialize_dut(name='DUT'): # Initialize a DUT
    clear()
    rmq = pv.ResourceManager()
    instruments = [dev for dev in rmq.list_resources()]

    print('\nAvailable devices:\n')

    for i,dev in enumerate(instruments):
        print(f'{i} ) {dev}')

    index = int(input(f'\nEnter the {name} index | '))

    clear()

    return instruments[index]

def pause(): # Pause script
    input('\nPress enter to continue. . .')

def clear(): # Clear terminal
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

# Standard Classes

class Fluke96270A():
    
    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.std = rm.open_resource(resource_address)

    def command(self,string): # Send an arbitrary command (Testing Purposes)
        self.std.write(string)

    def set_outp_mode(self,mode): # Select head or microwave output
        clear()
        if mode.lower() == 'microwave':
            self.std.write(':OUTP:ROUT MICR')
            print('\nOutput source set to Microwave')
            input('\nPress enter to continue. . .')
            clear()
        elif mode.lower() == 'head':
            self.std.write(':OUTP:ROUT HEAD')
            print('\nOutput source set to Leveling Head')
            input('\nPress enter to continue. . .')
            clear()
        else:
            print('\nInvalid output mode passed. Please enter either "head" or "microwave".')

    def sine_output(self,carrier,power): # Sine wave output
        self.std.write('OUTP OFF')
        self.std.write('INST SINE')
        self.std.write('UNIT:POW DBM')
        self.std.write(f'FREQ {carrier}')
        self.std.write(f'POW {power}')
        time.sleep(1)
        self.std.write('OUTP ON')

    def amplitude_modulation(self,carrier,power,rate,depth): # AM Output      
        self.std.write('OUTP OFF')
        self.std.write('INST AM')
        self.std.write('UNIT:POW DBM')
        self.std.write(f'POW {power}')
        self.std.write(f'FREQ {carrier}')
        self.std.write(f'AM:INT:FREQ {rate}')
        self.std.write(f'AM:DEPT {depth}')
        self.std.write('AM:STAT 1')
        time.sleep(1)
        self.std.write(f'OUTP ON')

    def frequency_modulation(self,carrier,power,rate,deviation): # FM Output      
        self.std.write('OUTP OFF')
        self.std.write('INST FM')
        self.std.write('UNIT:POW DBM')
        self.std.write(f'POW {power}')
        self.std.write(f'FREQ {carrier}')
        self.std.write(f'FM:INT:FREQ {rate}')
        self.std.write(f'FM:DEV {deviation}')
        self.std.write(f'FM:STAT 1')
        time.sleep(1)
        self.std.write(f'OUTP ON')

    def phase_modulation(self,carrier,power,rate,deviation): # PM Output
        self.std.write('OUTP OFF')
        self.std.write('INST PM')
        self.std.write('UNIT:POW DBM')
        self.std.write(f'POW {power}')
        self.std.write(f'FREQ {carrier}')
        self.std.write(f'PM:INT:FREQ {rate}')
        self.std.write(f'PM:DEV {deviation}')
        self.std.write('PM:STAT 1')
        time.sleep(1)
        self.std.write('OUTP ON')

    def silence(self): # Shhhhhhhhhhh
        self.std.write('OUTP OFF')

class Fluke9640A(Fluke96270A):
    
    def set_outp_mode(self, *args, **kwargs): # Overwriting unused method
        # This unit only outputs via leveling head
        pass

class HP33120A():

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.std = rm.open_resource(resource_address)
        self.std.write('*RST')
        self.std.write('VOLT:UNIT DBM')
        self.std.write('APPL:SIN 1e3,-20')

    def output_unit(self,unit='DBM'): # Options are VPP,VRMS, and DBM
        self.std.write(f'VOLT:UNIT {unit}')

    def sine_output(self,level,freq): # Sine wave output
        self.std.write(f'APPL:SIN {freq},{level}')

    def ramp_output(self,level,freq): # Triangle output
        self.std.write(f'APPL:RAMP {freq},{level}')

    def square_output(self,level,freq): # Square wave
        self.std.write(f'APPL:SQU {freq},{level}')

    def dc_output(self,voltage): # DC Output
        self.std.write(f'APPL:DC {voltage}')

    def dc_offset(self,offset_voltage): # DC Offset
        self.std.write(f'VOLT:OFFS {offset_voltage}')

class Fluke55XXA():

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.std = rm.open_resource(resource_address)

    # Basic Instrument Command Block

    def command(self,string): # Write an arbitrary command (testing purposes)
        self.std.write(string)

    def receive(self): # Read a output buffer. Broken. Test with pulling the *IDN? response
        self.std.read()

    def wave_shape(self,shape='SINE'): # Change AC Waveform Shape
        # Options | SINE, TRI, SQUARE, TRUNCS
        self.std.write(f'WAVE {shape}')

    def voltage_dc(self,voltage): # DCV Output
        self.std.write('STBY')
        self.std.write(f'OUT {voltage} V, 0 Hz')
        if voltage >= 33:
            self.std.write('*CLS')
            if voltage >= 100:
                #input('\n! High Voltage Warning ! Press enter to continue. . .')
                pass
        self.std.write('OPER')

    def voltage_ac(self,voltage,frequency): # ACV Output
        self.std.write('STBY')
        self.std.write(f'OUT {voltage} V, {frequency} Hz')
        if voltage >= 33:
            self.std.write('*CLS')
            if voltage >= 100:
                #input('\n! High Voltage Warning ! Press enter to continue. . .')
                pass
        self.std.write('OPER')

    def current_dc(self, current): # DCI Output
        self.std.write('STBY')
        self.std.write(f'OUT {current} A, 0 Hz')
        self.std.write('OPER')

    def current_ac(self,current,frequency): # ACI Output
        self.std.write('STBY')
        self.std.write(f'OUT {current} A, {frequency} Hz')
        self.std.write('LCOMP ON')
        self.std.write('OPER')

    def resistance_nocomp(self,resistance): # Resistance Output
        self.std.write('STBY')
        self.std.write(f'OUT {resistance} OHM')
        self.std.write('ZCOMP NONE')
        self.std.write('OPER')

    def resistance_2wire(self,resistance): # 2-Wire Resistance Output
        self.std.write('STBY')
        self.std.write(f'OUT {resistance} OHM')
        self.std.write('ZCOMP WIRE2')
        self.std.write('OPER')

    def resistance_4wire(self,resistance): # 4-Wire Resistance Output
        self.std.write('STBY')
        self.std.write(f'OUT {resistance} OHM')
        self.std.write('ZCOMP WIRE4')
        self.std.write('OPER')

    def capacitance(self,cap): # Capacitance Output
        self.std.write('STBY')
        self.std.write(f'OUT {cap} F')
        self.std.write('OPER')

    def thermocouple_temp(self,temp,unit='C',type='K'): # T/C Output
        self.std.write('STBY')
        self.std.write(f'TC_TYPE {type}')

        if unit=='F':
            self.std.write(f'OUT {temp} FAR')
        else:
            self.std.write(f'OUT {temp} CEL')

        
        self.std.write('OPER')

    def rtd_2wire_simulation(self,temp,unit='C',type='PT385'): # 2-Wire RTD Output
        self.std.write('STBY')

        if unit=='F':
            self.std.write(f'OUT {temp} FAR')
        else:
            self.std.write(f'OUT {temp} CEL')

        self.std.write(f'RTD_TYPE {type}')
        self.std.write('ZCOMP WIRE2')
        self.std.write('OPER')

    def rtd_4wire_simulation(self,temp,unit='C',type='PT385'): # 4-Wire RTD Output
        self.std.write('STBY')

        if unit=='F':
            self.std.write(f'OUT {temp} FAR')
        else:
            self.std.write(f'OUT {temp} CEL')

        self.std.write(f'RTD_TYPE {type}')
        self.std.write('ZCOMP WIRE4')
        self.std.write('OPER')

    def silence(self): # Shhhhhhhhhhhh
            self.std.write('STBY')
            time.sleep(0.5)

class HP4418B():
    
    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.std = rm.open_resource(resource_address)

    def write(self,command):
        self.std.write(command)

    def clear_errors(self):
        self.std.write('*CLS')

    def set_unit(self, unit='DBM'):
        # Options | W or DBM
        self.std.write(f'UNIT1:POW {unit}')

    def zero_sensor(self):
        clear()
        input('\nEnsure power sensor is disconnected. Press enter to continue. . .')
        print('\nZeroing the power sensor. . .')
        self.std.write('CAL1:ZERO:AUTO ONCE')
        time.sleep(10)
        input('\nSensor zeroed. Press enter to continue. . .')
        clear()
    
    def cal_sensor(self):
        clear()
        input('\nConnect power sensor to calibration output. Press enter to continue. . .')
        print('\nCalibrating sensor. . .')
        self.std.write('CAL1:AUTO ONCE')
        time.sleep(10)
        input('\nCalibration complete. Press enter to continue. . .')
        clear()

    def measure_power(self, freq, model='HP8482A'):      
        self.std.write('ABORt1')
        self.std.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.std.write(f'SENS1:CORR:CSET1:SEL "{model}"')
        self.std.write('SENS1:CORR:CSET1:STAT ON')
        self.std.write('SENSe1:FREQuency {:.6f}'.format(freq))
        self.std.write('INIT1')
        time.sleep(3)
        self.std.write('FETC1?')
        time.sleep(5)
        return float(self.std.read())

    def measure_power_w_corrections(self,correction):
        self.std.write('ABORt1')
        self.std.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.std.write(f'CAL1:RCF {correction:.2f}PCT')
        self.std.write('INIT1')
        time.sleep(5)
        self.std.write('FETC1?')
        time.sleep(3)
        return float(self.std.read())

    def load_corrections(self,inlist):
        from scipy.interpolate import interp1d
        df = pd.read_csv(inlist)
        corr_freqs = [float(a)*1e6 for a in df['Frequency']]
        corr_factors = [float(a) for a in df['Factor']]   
        return interp1d(corr_freqs, corr_factors, kind='cubic')

class Keithley2015():

    def __init__(self,resource_address):
        rm =pv.ResourceManager()
        self.std = rm.open_resource(resource_address)

    def command(self,string): # Send an arbitrary command (Testing Purposes)
        self.std.write(string)

    def query(self,string):
        return self.std.query(string)

    def stealth(self,status='OFF'): # Disable the display
        self.std.write(f'DISP:ENAB {status}')

    def set_to_dcv(self, range='AUTO',speed='MED'): # Set instrument to DCV      
        self.std.write('SENS:FUNC "VOLT:DC"')
        #self.std.write('INIT:CONT ON')

        if range == 'AUTO':
            self.std.write('SENS:VOLT:DC:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:VOLT:DC:RANG {range}')

        if speed == 'MED':
            self.std.write('SENS:VOLT:DC:NPLC 1')
        elif speed == 'SLOW':
            self.std.write('SENS:VOLT:DC:NPLC 10')
        else:
            self.std.write('SENS:VOLT:DC:NPLC 0.1')

        time.sleep(2)

    def set_to_acv(self, range='AUTO',speed='MED'): # Set instrument to ACV       
        self.std.write('SENS:FUNC "VOLT:AC"')

        if range == 'AUTO':
            self.std.write('SENS:VOLT:AC:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:VOLT:AC:RANG {range}')

        # Figure out how to change the rate on ACV mode
        time.sleep(2)

    def set_to_2wire_res(self, range='AUTO', speed='MED'): # Set instrument to 2 Wire Resistance
        self.std.write('SENS:FUNC "RES"')

        if range == 'AUTO':
            self.std.write('SENS:RES:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:RES:RANG {range}')
        time.sleep(2)

    def set_to_4wire_res(self, range='AUTO', speed='MED'): # Set instrument to 4 Wire Resistance
        self.std.write('SENS:FUNC "FRES"')

        if range == 'AUTO':
            self.std.write('SENS:FRES:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:FRES:RANG {range}')
        time.sleep(2)

    def set_to_aci(self, range='AUTO', speed='MED'): # Set instrument to ACI
        self.std.write('SENS:FUNC "CURR:AC"')
        #self.std.write('INIT:CONT ON')

        if range == 'AUTO':
            self.std.write('SENS:CURR:AC:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:CURR:AC:RANG {range}')

        # Figure out how to change the rate on ACImode
        time.sleep(2)

    def set_to_dci(self, range='AUTO', speed='MED'): # Set instrument to DCI
        self.std.write('SENS:FUNC "CURR:DC"')

        if range == 'AUTO':
            self.std.write('SENS:CURR:DC:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:CURR:DC:RANG {range}')
        time.sleep(2)

    def set_to_freq(self):
        self.std.write('SENS:FUNC "FREQ"')
        time.sleep(2)

    def set_to_thermocouple(self,type='J'):
        self.std.write('SENS:FUNC "TEMP"')
        self.std.write(f'SENS:TEMP:TC:TYPE {type}')
        time.sleep(2)

    def read(self): # Read instrument current value
        self.std.write('INIT:CONT ON')
        reading = self.std.query('FETC?')
        return float(reading)

    def slow_read(self): # Read instrument current value
        self.std.write('INIT:CONT ON')
        time.sleep(20)
        reading = self.std.query('FETC?')
        time.sleep(20)
        return float(reading)

    def set_ac_averaging(self, naverages=10): # Set number of readings for the moving average filter
        self.std.write(f'SENS:VOLT:AVER:COUN {naverages}')

class Keithley2001(Keithley2015):

    def set_to_acv(self, range='AUTO',speed='MED', detector='RMS'): # Set instrument to ACV       
        self.std.write('SENS:FUNC "VOLT:AC"')
        # Avaliable modes | RMS, AVERage, LFRMs, NPeak, PPeak
        self.std.write(f'SENS:VOLT:AC:DET:FUNC {detector}')

        if range == 'AUTO':
            self.std.write('SENS:VOLT:AC:RANG:AUTO 1')
        else:
            self.std.write(f'SENS:VOLT:AC:RANG {range}')

        # Figure out how to change the rate on ACV mode
        time.sleep(2)

    def set_to_thermocouple(self,type='J'):
        self.std.write('SENS:FUNC "TEMP"')
        self.std.write('SENS:TEMP:TRAN TC')
        self.std.write(f'SENS:TEMP:TC:TYPE {type}')
        time.sleep(2)

    def set_to_4_wire_rtd(self, type='PT385'):
        self.std.write('SENS:FUNC "TEMP"')
        self.std.write('SENS:TEMP:TRAN FRTD')
        self.std.write(f'SENS:TEMP:RTD:TYPE {type}')
        time.sleep(2)

    def set_to_2_wire_rtd(self, type='PT385'):
        self.std.write('SENS:FUNC "TEMP"')
        self.std.write('SENS:TEMP:TRAN RTD')
        self.std.write(f'SENS:TEMP:RTD:TYPE {type}')
        time.sleep(2)

    def read(self): # Read instrument current value
        self.std.write('INIT:CONT ON')
        result_string = self.std.query('FETC?')
        msmnt = re.search('\S+[Ee][+-]?\d\d', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)

    def slow_read(self):
        self.std.write('INIT:CONT ON')
        time.sleep(20)
        result_string = self.std.query('FETC?')
        msmnt = re.search('\S+[Ee][+-]?\d\d', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)

class HP3458A():

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.std = rm.open_resource(resource_address)

    def command(self,string):
        self.std.write(string)

    def auto_cal(self):
        self.std.write('ACAL')

    def nplc(self,nplc):
        self.std.write(f'NPLC {nplc}')    

    def set_to_dcv(self, range='AUTO', nplc=10):
        self.std.write(f'DCV,{range} ; NPLC {nplc}')

    def msg(self,string):
        self.std.write(f'DISP MSG "{string}"')

    def read(self): # Broken 
        self.std.write('OFORMAT DINT')
        self.std.write('TARM SGL,1')
        time.sleep(5)
        reading = self.std.read()
        return reading
