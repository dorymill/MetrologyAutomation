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

    def receive(self): # Broken. Test with reading *IDN? String
        self.std.read()

    def multifreq_multilevel(self,inlist): # This will sweep through a list of given levels given different frequencies
        clear()

        self.std.write('OUTP OFF')
        df = pd.read_csv(inlist)

        freqs = [float(a) for a in df['Frequency']]
        power = [float(a) for a in df['Power']]

        freqs = [f for f in freqs if math.isnan(f) is False]
        power = [p for p in power if math.isnan(p) is False]

        for f in freqs:
            self.std.write(f'FREQ {f}')
            for p in power:
                self.std.write(f'POW {p}')
                self.std.write('OUTP ON')

                print(f'\nCurrent Point: {p:.2f} dBm {f/1e6:.3f} MHz')
                input('\nPress enter to continue. . .')
                self.std.write('OUTP OFF')
                time.sleep(0.5)
                clear()
                
        input('\nSweep complete! Press any key to continue. . .')

    def freq_sweep_usr(self): # This will sweep at a given level through a given frequency range in given steps...
        clear()

        self.std.write('OUTP OFF')
        input('\nConnect 96270A to DUT. Press any key to continue. . .')
        a = float(input('\nEnter start frequency | '))
        b  = float(input('\nEnter stop frequency | '))
        res = float(input('\nEnter resolution | '))
        power = float(input('\nEnter power (dBm) | '))
        clear()

        steps = (b-a) / res
        a = int(a)
        b = int(b)
        steps = int(steps) + 1
        freq = np.linspace(a,b,steps)

        for i in range(len(freq)):
            self.std.write(f'POW {power}')
            self.std.write(f'FREQ {freq[i]}')
            self.std.write('OUTP ON')
            print('\nCurrent Frequency | {:.3f} MHz'.format(freq[i]/1e6))
            input('\nPress enter to continue. . .')
            self.std.write('OUTP OFF')
            time.sleep(0.5)
            clear()

        input('\nSweep complete. Press any key to continue. . .')
        clear()

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

    def freq_sweep_usr(self): # Sweeps in equal steps given range and resolution
        clear()

        a = float(input('\nEnter start frequency | '))
        b  = float(input('\nEnter stop frequency | '))
        res = float(input('\nEnter resolution | '))
        clear()

        steps = (b-a) / res
        a = int(a)
        b = int(b)
        steps = int(steps) + 1

        freq = np.linspace(a,b,steps)
        p = np.empty(shape=len(freq))

        for i in range(len(freq)):
            self.std.write('APPL:SIN {:.6f},0'.format(freq[i]))
            print('\nCurrent Frequency | {:.3f} MHz'.format(freq[i]/1e6))
            input('\nPress any key to continue. . .')
            clear()

        input('\nSweep complete. Press any key to continue. . .')
        clear()

    def multifreq_multilevel(self,inlist): # This will sweep through a list of given levels given different frequencies
        clear()

        df = pd.read_csv(inlist)

        freqs = [float(a) for a in df['Frequency']]
        power = [float(a) for a in df['Power']]

        freqs = [f for f in freqs if math.isnan(f) == False]
        power = [p for p in power if math.isnan(p) == False]

        for f in freqs:
            for p in power:
                self.std.write(f'APPL:SIN {f}, {p}')

                print(f'\nCurrent Point: {p:.2f} dBm at {f/1e6:.3f} MHz')
                input('\nPress enter to continue. . .')
                clear()

        self.std.write('APPL:SIN 50000000,-20')
        input('\nSweep complete. Press any key to continue. . .')
        clear()

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

    # Basic Test Logic Block
    # All verification tests should call use the self class and not self.std
    # self.std is reserved for visa methods

    def acv_verify(self,inlist): # ACV Verification Test
        self.silence()
        print('\nSet DUT to read AC Voltage. Press enter to continue. . .')
        input()
        clear()

        
        df = pd.read_csv(inlist)

        voltage_ac = df['Voltage']
        freq = df['Frequency']
        voltage_ac = [float(v) for v in voltage_ac]
        freq = [float(f) for f in freq]
        acv_read = []

        print('\nCurrent Test | AC Voltage\n\nConnect calibrator voltage output to DUT input.\nPress enter to continue. . .')
        input()
        clear()

        for i,v in enumerate(voltage_ac):
            print('\nCurrent Test | AC Voltage\n')
            self.voltage_ac(v,freq[i])
            print(f'\nCurrent Point: {v:.3f} V at {freq[i]:.0f} Hz')
            result = input('\nEnter DUT reading | ')
            acv_read.append(result)
            if i <= len(voltage_ac)-2:
                input(f'\nNext point is {voltage_ac[i+1]} V at {freq[i+1]/1000} kHz. Set DUT range before continuing. Press enter when done. . .')
            clear()
        return acv_read

    def dcv_verify(self,inlist): # DCV Verification Test
        self.silence()
        print('\nSet DUT to read DC Voltage. Press enter to continue. . .')
        input()
        clear()

        # DC Voltage Test
        df = pd.read_csv(inlist)

        voltage_dc = df['Voltage']
        voltage_dc = [float(v) for v in voltage_dc]
        dcv_read = []

        for i,v in enumerate(voltage_dc):
            print('\nCurrent Test | DC Voltage\n')
            self.voltage_dc(v)
            print(f'\nCurrent Point: {v:.3f} V')
            result = input('\nEnter DUT reading | ')
            dcv_read.append(result)
            if i <= len(voltage_dc)-2:
                input(f'\nNext point is {voltage_dc[i+1]} V. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return dcv_read

    def acmv_verify(self,inlist): # ACmV Verification Test
        self.silence()
        print('\nSet DUT to read AC miliVolts. Press enter to continue. . .')
        input()
        clear()

        # AC mV
        df = pd.read_csv(inlist)

        voltage_acmv = df['Voltage']
        freq = df['Frequency']
        voltage_acmv = [float(v) for v in voltage_acmv]
        freq = [float(f) for f in freq]

        acmv_read = []

        for i,v in enumerate(voltage_acmv):
            print('\nCurrent Test | AC miliVolt\n')
            self.voltage_ac(v,freq[i])
            print(f'\nCurrent Point: {v*1000:.3f} mV at {freq[i]:.0f} Hz')
            result = input('\nEnter DUT reading | ')
            acmv_read.append(result)
            if i <= len(voltage_acmv)-2:
                input(f'\nNext point is {voltage_acmv[i+1]*1000:.3f}mV. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return acmv_read

    def dcmv_verify(self,inlist): # DCmV Verification Test
        self.silence()
        print('\nSet DUT to read DC miliVolts. Press enter to continue. . .')
        input()
        clear()

        # DC mV
        df = pd.read_csv(inlist)

        voltage_dcmv = df['Voltage']
        voltage_dcmv = [float(v) for v in voltage_dcmv]
        dcmv_read = []

        for i,v in enumerate(voltage_dcmv):
            print('\nCurrent Test | DC miliVolt\n')
            self.voltage_dc(v)
            print(f'\nCurrent Point: {v*1000:.3f} mV')
            result = input('\nEnter DUT reading | ')
            dcmv_read.append(result)
            if i <= len(voltage_dcmv)-2:
                input(f'\nNext point is {voltage_dcmv[i+1]*1000:.3f} mV. Set DUT range before continuing. Press enter when done. . .')
            clear()
        
        return dcmv_read

    def resistance_nocomp_verify(self,inlist): # Resistance Verification Test
        self.silence()
        print('\nSet DUT to read Resistance. Press enter to continue. . .')
        input()
        clear()

        # Resistance
        df = pd.read_csv(inlist)

        res_nom = df['Resistance']
        res_nom = [float(r) for r in res_nom]
        res_read = []

        for i,r in enumerate(res_nom):
            print('\nCurrent Test | Resistance\n')
            self.resistance_nocomp(r)
            print(f'\nCurrent Point: {r:.3f} Ohms')
            result = input('\nEnter DUT reading | ')
            res_read.append(result)
            if i <= len(res_nom)-2:
                input(f'\nNext point is {res_nom[i+1]} Ohms. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return res_read

    def resistance_2wire_verify(self,inlist): # Resistance Verification Test
        self.silence()
        print('\nSet DUT to read 2-Wire Resistance. Press enter to continue. . .')
        input()
        clear()

        # Resistance
        df = pd.read_csv(inlist)

        res_nom = df['Resistance']
        res_nom = [float(r) for r in res_nom]
        res_read = []

        for i,r in enumerate(res_nom):
            print('\nCurrent Test | Resistance\n')
            self.resistance_2wire(r)
            print(f'\nCurrent Point: {r:.3f} Ohms')
            result = input('\nEnter DUT reading | ')
            res_read.append(result)
            if i <= len(res_nom)-2:
                input(f'\nNext point is {res_nom[i+1]} Ohms. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return res_read

    def resistance_4wire_verify(self,inlist): # Resistance Verification Test
        self.silence()
        print('\nSet DUT to read 4-Wire Resistance. Press enter to continue. . .')
        input()
        clear()

        # Resistance
        df = pd.read_csv(inlist)

        res_nom = df['Resistance']
        res_nom = [float(r) for r in res_nom]
        res_read = []

        for i,r in enumerate(res_nom):
            print('\nCurrent Test | Resistance\n')
            self.resistance_4wire(r)
            print(f'\nCurrent Point: {r:.3f} Ohms')
            result = input('\nEnter DUT reading | ')
            res_read.append(result)
            if i <= len(res_nom)-2:
                input(f'\nNext point is {res_nom[i+1]} Ohms. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return res_read

    def capacitance_verify(self,inlist): # Capacitance Verification Test
        self.silence()
        print('\nSet DUT to read Capacitance. Press enter to continue. . .')
        input()
        clear()

        df = pd.read_csv(inlist)

        capacitance_noms = df['Capacitance']
        capacitance_noms = [float(c) for c in capacitance_noms]
        cap_read = []

        for i,c in enumerate(capacitance_noms):
            print('\nCurrent Test | Capacitance\n')
            if c == 0:
                print('\nDisconnect leads from DUT for this test.')
                self.command('*RST')
                self.command('STBY')
            else:
                self.capacitance(c)
            print(f'\nCurrent Point: {c*1e6:.6f} µF')
            result = input('\nEnter DUT reading | ')
            cap_read.append(result)
            if i <= len(capacitance_noms)-2:
                input(f'\nNext point is {capacitance_noms[i+1]*1e6} µF. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return cap_read

    def dci_verify(self,inlist): # DCI Verification Test
        self.silence()
        print('\nSet DUT to read DC Current. Press enter to continue. . .')
        input()
        clear()

        df = pd.read_csv(inlist)

        dci_noms = df['Current']
        dci_noms = [float(a) for a in dci_noms]

        dci_read = []

        print('\nCurrent Test | DC Current\n\nConnect calibrator current output to DUT input.\nPress enter to continue. . .')
        input()
        clear()

        for i,a in enumerate(dci_noms):
            print('\nCurrent Test | DC Current\n')
            self.current_dc(a)
            print(f'\nCurrent Point: {a:.3f} A')
            result = input('\nEnter DUT reading | ')
            dci_read.append(result)
            if i <= len(dci_noms)-2:
                input(f'\nNext point is {dci_noms[i+1]} A. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return dci_read

    def aci_verify(self,inlist): # ACI Verification Test
        self.silence()
        print('\nSet DUT to read AC Current. Press enter to continue. . .')
        input()
        clear()

        df = pd.read_csv(inlist)

        aci_noms = df['Current']
        freq = df['Frequency']
        aci_noms = [float(a) for a in aci_noms]
        freq = [float(f) for f in freq]

        aci_read = []

        for i,a in enumerate(aci_noms):
            print('\nCurrent Test | AC Current\n')
            self.current_ac(a,freq[i])
            print(f'\nCurrent Point: {a:.3f} A at {freq[i]:.0f} Hz')
            result = input('\nEnter DUT reading | ')
            aci_read.append(result)
            if i <= len(aci_noms)-2:
                input(f'\nNext point is {aci_noms[i+1]:.3f} A. Set DUT range before continuing. Press enter when done. . .')
            clear()

        return aci_read

    # Model Specific Tests
    # Files with new classes called [StandardClassName]SpecificInstrunctions should be made
    # such that model specific functions can be inherited into the 
    # respective standard's class definitions

    # Fluke 115

    def continuity_verify_fluke115(self):
        self.std.silence()
        print('\nSet DUT to Continuity. Press enter to continue. . .')
        input()
        clear()

        # Continuity
        # Beep On
        print('\nCurrent Test | Continuity\n')
        self.std.resistance_nocomp(20)
        print('\nCurrent Point: 20 Ohms')
        beep_on_result = input('\nEnter PASS or FAIL | ')
        # Beep Off
        clear()
        print('\nCurrent Test | Continuity\n')
        self.std.resistance_nocomp(250)
        print('\nCurrent Point: 250 Ohms')
        beep_off_result = input('\nEnter PASS or FAIL | ')
        clear()

        cont_read = []
        cont_read.append(beep_on_result)
        cont_read.append(beep_off_result)

        return cont_read

    def auxiliary_verify_fluke115(self):
        self.std.command('*RST')

        print('\nCurrent Test | Keypad, Display, and Backlight\n\nDisconnect calibrator from DUT.\nPress enter to continue. . .')
        input()
        clear()

        print('\nCurrent Test | Keypad')
        keypad_results = input('\nEnter PASS or FAIL | ')
        clear()

        print('\nCurrent Test | Display')
        display_results = input('\nEnter PASS or FAIL | ')
        clear()

        print('\nCurrent Test | Backlight')
        backlight_results = input('\nEnter PASS or FAIL | ')
        clear()

        aux_read = []
        aux_read.append(keypad_results)
        aux_read.append(display_results)
        aux_read.append(backlight_results)

        return aux_read

class HP8482A():
    
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
        input('\nEnsure power sensor is disconnected. Press any key to continue. . .')
        print('\nZeroing the power sensor. . .')
        self.std.write('CAL1:ZERO:AUTO ONCE')
        time.sleep(10)
        input('\nSensor zeroed. Press any key to continue. . .')
        clear()
    
    def cal_sensor(self):
        clear()
        input('\nConnect power sensor to calibration output. Press any key to continue. . .')
        print('\nCalibrating sensor. . .')
        self.std.write('CAL1:AUTO ONCE')
        time.sleep(10)
        input('\nCalibration complete. Press any key to continue. . .')
        clear()

    def measure_power(self, freq):      
        self.std.write('ABORt1')
        self.std.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.std.write('SENS1:CORR:CSET1:SEL "HP8482A"')
        self.std.write('SENS1:CORR:CSET1:STAT ON')
        self.std.write('SENSe1:FREQuency {:.6f}'.format(freq))
        self.std.write('INIT1')
        time.sleep(3)
        self.std.write('FETC1?')
        time.sleep(5)
        power = float(self.std.read())
        return power

    def measure_power_w_corrections(self,correction):
        self.std.write('ABORt1')
        self.std.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.std.write(f'CAL1:RCF {correction:.2f}PCT')
        self.std.write('INIT1')
        time.sleep(5)
        self.std.write('FETC1?')
        time.sleep(3)
        power = float(self.std.read())
        return power

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
        #self.std.write('INIT:CONT ON')

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

    def read(self): # Read instrument current value
        self.std.write('INIT:CONT ON')
        self.std.write('FETC?')
        time.sleep(1)
        return float(self.std.read())

class Keithley2001(Keithley2015):

    def read(self): # Read instrument current value
        self.std.write('INIT:CONT ON')
        time.sleep(1)
        self.std.write('FETC?')
        time.sleep(1)
        result_string = self.std.read()
        msmnt = re.search('[+-]?\d+.\d+E[+-]?\d+', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)
