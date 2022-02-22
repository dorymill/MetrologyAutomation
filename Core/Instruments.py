##########################################################
#                                                        #
#                                                        #
#     Metrology Test Automation Instrument Core          #
#                                                        #
#             created by Doryan Miller                   #
#                                                        #
#                                                        #
##########################################################
import time, re, os
import pyvisa as pv
import pandas as pd
from scipy.interpolate import interp1d

# Common Functions

def initialize_ins(name='{instrument name}'): # Initialize an instrument
    '''Instantiates the PyVISA resource manager, queries the controller, and returns all seen instruments, pending user input on which to initialize.'''
    clear()
    rmq = pv.ResourceManager()
    instruments = [dev for dev in rmq.list_resources()]

    print('\nAvailable devices:\n')

    for i,dev in enumerate(instruments):
        print(f'{i} ) {dev}')

    index1 = int(input(f"\nEnter the {name}'s index | "))
    clear()

    return instruments[index1]

def pause(): # Pause script
    '''Pause the script.'''
    input('\nPress enter to continue. . .')

def clear(): # Clear terminal
    '''Clear terminal output based on operating system.'''
    os.system('cls' if os.name == 'nt' else 'clear')

def swap(message): # Halt and message
    '''Halt script and display a message. Usually used for cable and instrument swaps.'''
    clear()
    print(f'\n{message}')
    pause()
    clear()

# Instrument Classes

# Standards
class Init(): # Initializer Parent Class

    '''Parent class containg the basic initialization routine and common instrument commands.'''

    def __init__(self,resource_address): # Initialize instrument through PyVisa
        '''Initializes an instrument. Timeout may need varied dependent upon the nature of the instrument.'''
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.timeout = 60e3

    def command(self,string): # Send and arbitrary command
        '''Sends a general command string to an instrument. Typically for seldom used commands that don't merit their own method.'''
        self.ins.write(string)

    def query(self,string): # Send an arbitrary query
        '''Sends a general command and reads the instrument response. Typically use to collect data.'''
        return self.ins.query(string)

class Fluke96270A(Init): # RF Reference Source
  
    '''Fluke 96720A Low Phase Noise Radio Frequency Reference Source'''

    def set_outp_mode(self,mode): # Select head or microwave output
        '''Sets output mode to microwave or leveling head.'''
        clear()
        if mode.lower() == 'microwave':
            self.ins.write(':OUTP:ROUT MICR')
        elif mode.lower() == 'head':
            self.ins.write(':OUTP:ROUT HEAD')
        else:
            print('\nInvalid output mode passed. Please enter either "head" or "microwave".')

    def sine_output(self,carrier,power): # Sine wave output
        '''Sets sine output to a given power and frequency and engages output.'''
        self.ins.write('OUTP OFF')
        self.ins.write('INST SINE')
        self.ins.write('UNIT:POW DBM')
        self.ins.write(f'FREQ {carrier}')
        self.ins.write(f'POW {power}')
        time.sleep(1)
        self.ins.write('OUTP ON')

    def amplitude_modulation(self,carrier,power,rate,depth): # AM Output
        '''Sets output to amplitude modulation at a given carrier, power, rate, and depth then engages the output.'''    
        self.ins.write('OUTP OFF')
        self.ins.write('INST AM')
        self.ins.write('UNIT:POW DBM')
        self.ins.write(f'POW {power}')
        self.ins.write(f'FREQ {carrier}')
        self.ins.write(f'AM:INT:FREQ {rate}')
        self.ins.write(f'AM:DEPT {depth}')
        self.ins.write('AM:STAT 1')
        time.sleep(1)
        self.ins.write(f'OUTP ON')

    def frequency_modulation(self,carrier,power,rate,deviation): # FM Output
        '''Sets output to frequency modulation at a given carrier, power, rate, and deviation then engages output.'''
        self.ins.write('OUTP OFF')
        self.ins.write('INST FM')
        self.ins.write('UNIT:POW DBM')
        self.ins.write(f'POW {power}')
        self.ins.write(f'FREQ {carrier}')
        self.ins.write(f'FM:INT:FREQ {rate}')
        self.ins.write(f'FM:DEV {deviation}')
        self.ins.write(f'FM:STAT 1')
        time.sleep(1)
        self.ins.write(f'OUTP ON')

    def phase_modulation(self,carrier,power,rate,deviation): # PM Output
        '''Sets output to phase modulation at a given carrier, power, rate, and deviation then engages output.'''
        self.ins.write('OUTP OFF')
        self.ins.write('INST PM')
        self.ins.write('UNIT:POW DBM')
        self.ins.write(f'POW {power}')
        self.ins.write(f'FREQ {carrier}')
        self.ins.write(f'PM:INT:FREQ {rate}')
        self.ins.write(f'PM:DEV {deviation}')
        self.ins.write('PM:STAT 1')
        time.sleep(1)
        self.ins.write('OUTP ON')

    def silence(self): # Shhhhhhhhhhh
        '''Disengages output.'''
        self.ins.write('OUTP OFF')

class Fluke9640A(Fluke96270A,Init): # RF Reference Source
  
    '''Fluke 9640A Radio Frequency Reference Source'''    

    def set_outp_mode(self, *args, **kwargs): # Overwriting unused method
        '''Method not applicable to this unit.'''
        # This unit only outputs via leveling head
        pass

class HP33120A(Init): # Signal Generator

    '''HP 33120A 15 MHz Signal Generator'''

    def __init__(self,resource_address): # Initialization constructor
        '''Init method redefined to set unit to minimum output on successful connection.'''
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.write('*RST')
        self.ins.write('VOLT:UNIT DBM')
        self.ins.write('APPL:SIN 1e3,-20')

    def output_unit(self,unit='DBM'): # Options are VPP,VRMS, and DBM
        '''Sets the output unit.'''
        self.ins.write(f'VOLT:UNIT {unit}')

    def sine_output(self,level,freq): # Sine wave output
        '''Sets the unit to sine wave output.'''
        self.ins.write(f'APPL:SIN {freq},{level}')

    def ramp_output(self,level,freq): # Triangle output
        '''Sets the unit to ramp wave output.'''
        self.ins.write(f'APPL:RAMP {freq},{level}')

    def square_output(self,level,freq): # Square wave
        '''Sets the unit to square wave output.'''
        self.ins.write(f'APPL:SQU {freq},{level}')

    def dc_output(self,voltage): # DC Output
        '''Sets the unit to DC voltage output.'''
        self.ins.write(f'APPL:DC {voltage}')

    def dc_offset(self,offset_voltage): # DC Offset
        '''Sets the signal DC offset voltage.'''
        self.ins.write(f'VOLT:OFFS {offset_voltage}')

class Fluke55XXA(Init): # Multifunction Calibrator

    '''Fluke 55XXA Multifunction Calibrator. Refer to manual for approriate ranges.'''

    def wave_shape(self,shape='SINE'): # Change AC Waveform Shape
        '''Sets the wave shape.'''
        # Options | SINE, TRI, SQUARE, TRUNCS
        self.ins.write(f'WAVE {shape}')

    def voltage_dc(self,voltage): # DCV Output
        '''Sets the unit to output a specified DC voltage.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {voltage} V, 0 Hz')
        if voltage >= 33:
            self.ins.write('*CLS')
            if voltage >= 100:
                #input('\n! High Voltage Warning ! Press enter to continue. . .')
                pass
        self.ins.write('OPER')

    def voltage_ac(self,voltage,frequency): # ACV Output
        '''Sets the unit to output a specified AC voltage.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {voltage} V, {frequency} Hz')
        if voltage >= 33:
            self.ins.write('*CLS')
            if voltage >= 100:
                #input('\n! High Voltage Warning ! Press enter to continue. . .')
                pass
        self.ins.write('OPER')

    def current_dc(self, current): # DCI Output
        '''Sets the unit to output a specified DC current.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {current} A, 0 Hz')
        self.ins.write('OPER')

    def current_ac(self,current,frequency): # ACI Output
        '''Sets the unit to output a specified AC current.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {current} A, {frequency} Hz')
        self.ins.write('LCOMP ON')
        self.ins.write('OPER')

    def resistance_nocomp(self,resistance): # Resistance Output
        '''Sets the unit to output a specified resistance with no compensation.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {resistance} OHM')
        self.ins.write('ZCOMP NONE')
        self.ins.write('OPER')

    def resistance_2wire(self,resistance): # 2-Wire Resistance Output
        '''Sets the unit to output a specified resistance with 2-wire compensation.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {resistance} OHM')
        self.ins.write('ZCOMP WIRE2')
        self.ins.write('OPER')

    def resistance_4wire(self,resistance): # 4-Wire Resistance Output
        '''Sets the unit to output a specified resistance with 4-wire compensation.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {resistance} OHM')
        self.ins.write('ZCOMP WIRE4')
        self.ins.write('OPER')

    def capacitance(self,cap): # Capacitance Output
        '''Sets the unit to output a specified capacitance.'''
        self.ins.write('STBY')
        self.ins.write(f'OUT {cap} F')
        self.ins.write('OPER')

    def thermocouple_temp(self,temp,unit='C',tctype='K'): # T/C Output
        '''Sets the unit to output a specified temperature via specified T/C type.'''
        self.ins.write('STBY')
        self.ins.write(f'TC_TYPE {tctype}')

        if unit=='F':
            self.ins.write(f'OUT {temp} FAR')
        else:
            self.ins.write(f'OUT {temp} CEL')

        
        self.ins.write('OPER')

    def rtd_2wire_simulation(self,temp,unit='C',tctype='PT385'): # 2-Wire RTD Output
        '''Sets the unit to output a specified temperature via specified 2-wire RTD type.'''
        self.ins.write('STBY')

        if unit=='F':
            self.ins.write(f'OUT {temp} FAR')
        else:
            self.ins.write(f'OUT {temp} CEL')

        self.ins.write(f'RTD_TYPE {tctype}')
        self.ins.write('ZCOMP WIRE2')
        self.ins.write('OPER')

    def rtd_4wire_simulation(self,temp,unit='C',tctype='PT385'): # 4-Wire RTD Output
        '''Sets the unit to output a specified temperature via specified 4-wire RTD type.'''
        self.ins.write('STBY')

        if unit=='F':
            self.ins.write(f'OUT {temp} FAR')
        else:
            self.ins.write(f'OUT {temp} CEL')

        self.ins.write(f'RTD_TYPE {tctype}')
        self.ins.write('ZCOMP WIRE4')
        self.ins.write('OPER')

    def silence(self): # Shhhhhhhhhhhh
        '''Disengages unit output.'''
        self.ins.write('STBY')

class HP4418B(Init): # RF Power Meter

    '''HP 4418B EPM Series Power Meter'''

    def clear_errors(self): # Clear error register
        '''Clears the unit error register.'''
        self.ins.write('*CLS')

    def set_unit(self, unit='DBM'): # Set output unit
        '''Sets the unit of measure.'''
        # Options | W or DBM
        self.ins.write(f'UNIT1:POW {unit}')

    def zero_sensor(self): # Zero power sensor
        '''Zeroes the power sensor.'''
        clear()
        input('\nEnsure power sensor is disconnected.\nPress enter to continue. . .')
        clear()
        print('\nZeroing the power sensor. . .')
        self.ins.write('CAL1:ZERO:AUTO ONCE')
        time.sleep(10)
        clear()
        input('\nSensor zeroed.\nPress enter to continue. . .')
        clear()
    
    def cal_sensor(self): # Calibrate Power Sensor
        '''Calibrates the power sensor.'''
        clear()
        input('\nConnect power sensor to calibration output.\nPress enter to continue. . .')
        clear()
        print('\nCalibrating sensor. . .')
        self.ins.write('CAL1:AUTO ONCE')
        time.sleep(10)
        clear()
        input('\nCalibration complete.\nPress enter to continue. . .')
        clear()

    def measure_power(self, freq, model='HP8482A'): # Measure power w/internal corrections
        '''Measures power with default corrections for the specified sensor model. Only use with new power sensors.'''
        self.ins.write('ABORt1')
        self.ins.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.ins.write(f'SENS1:CORR:CSET1:SEL "{model}"')
        self.ins.write('SENS1:CORR:CSET1:STAT ON')
        self.ins.write(f'SENSe1:FREQuency {freq:.6f}')
        self.ins.write('INIT1')
        time.sleep(5)     
        return float(self.ins.query('FETC1?'))

    def measure_power_w_corrections(self,correction): # Measure power with given corrections
        '''Measures power with user provided corrections. See load_corrections method.'''
        self.ins.write('ABORt1')
        self.ins.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.ins.write(f'CAL1:RCF {correction:.2f}PCT')
        self.ins.write('INIT1')
        time.sleep(5)
        return float(self.ins.query('FETC?'))

    def load_corrections(self,inlist): # Load correction factors
        '''Loads user defined correction factors and returns an object that takes in a frequency and outputs a correction factor. Does not extrapolate.'''
        df = pd.read_csv(inlist)
        corr_freqs = [float(a)*1e6 for a in df['Frequency']]
        corr_factors = [float(a) for a in df['Factor']]   
        return interp1d(corr_freqs, corr_factors, kind='cubic')

class Keithley2015(Init): # Digital Multimeter

    '''Keithley 2015 Digital Multimeter'''

    def stealth(self, status='OFF'): # Disable the display
        '''Disable the display.'''
        self.ins.write(f'DISP:ENAB {status}')

    def set_to_dcv(self, speed='AUTO', vrange='AUTO'): # Set instrument to DCV     
        '''Set the unit to measure DC Voltage.''' 
        self.ins.write('SENS:FUNC "VOLT:DC"')
        #self.ins.write('INIT:CONT ON')

        if vrange == 'AUTO':
            self.ins.write('SENS:VOLT:DC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:VOLT:DC:RANG {vrange}')

        if speed == 'MED':
            self.ins.write('SENS:VOLT:DC:NPLC 1')
        elif speed == 'SLOW':
            self.ins.write('SENS:VOLT:DC:NPLC 10')
        else:
            self.ins.write('SENS:VOLT:DC:NPLC 0.1')


    def set_to_acv(self, vrange='AUTO'): # Set instrument to ACV    
        '''Set the unit to measure AC Voltage.'''   
        self.ins.write('SENS:FUNC "VOLT:AC"')
        self.ins.write('UNIT:VOLT:AC V')

        if vrange == 'AUTO':
            self.ins.write('SENS:VOLT:AC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:VOLT:AC:RANG {vrange}')


    def set_to_dbm(self, impedance=50): # Set to dBm mode
        '''Set the unit to measure AC Voltage in dBm mode.'''
        self.set_to_acv()
        self.ins.write(f'UNIT:VOLT:AC:DBM:IMP {impedance}')
        self.ins.write('UNIT:VOLT:AC DBM')

    def set_to_THD(self, frequency, unit='dB'): # Set to Total Harmonic Distortion mode
        '''Set the unit to measure total harmonic distortion in given units.'''
        if unit == '%':
            self.ins.write('SENS:FUNC "DIST"')
            self.ins.write(f'SENS:DIST:FREQ {frequency}')
        else:
            self.ins.write('SENS:FUNC "DIST"')
            self.ins.write('SENS:DIST:TYPE SINAD')
            self.ins.write('SENS:DIST:TYPE THD')
            self.ins.write(f'SENS:DIST:FREQ {frequency}')

    def thd_freq(self,frequency): # Set THD frequency
        '''Tunes the carrier frequency for distortion measurements.'''
        self.ins.write(f'SENS:DIST:FREQ {frequency}')

    def set_to_2wire_res(self, resrange='AUTO', speed='MED'): # Set instrument to 2 Wire Resistance
        '''Set the unit to measure 2-wire resistance.'''
        self.ins.write('SENS:FUNC "RES"')

        if resrange == 'AUTO':
            self.ins.write('SENS:RES:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:RES:RANG {resrange}')


    def set_to_4wire_res(self, resrange='AUTO', speed='MED'): # Set instrument to 4 Wire Resistance
        '''Set the unit to measure 4-wire resistance.'''
        self.ins.write('SENS:FUNC "FRES"')

        if resrange == 'AUTO':
            self.ins.write('SENS:FRES:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:FRES:RANG {resrange}')


    def set_to_aci(self, irange='AUTO', speed='MED'): # Set instrument to ACI
        '''Set the unit to measure AC Current.'''
        self.ins.write('SENS:FUNC "CURR:AC"')
        #self.ins.write('INIT:CONT ON')

        if irange == 'AUTO':
            self.ins.write('SENS:CURR:AC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:CURR:AC:RANG {irange}')

    def set_to_dci(self, irange='AUTO', speed='MED'): # Set instrument to DCI
        '''Set the unit to measure DC Current.'''
        self.ins.write('SENS:FUNC "CURR:DC"')

        if irange == 'AUTO':
            self.ins.write('SENS:CURR:DC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:CURR:DC:RANG {irange}')
        time.sleep(2)

    def set_to_freq(self): # Set instrument to Frequency
        '''Set the unit to measure Frequency.'''
        self.ins.write('SENS:FUNC "FREQ"')
        time.sleep(2)

    def set_to_thermocouple(self,tctype='J'): # Set instrument to Thermocouple
        '''Set the unit to measure T/C temperature.'''
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write(f'SENS:TEMP:TC:TYPE {tctype}')
        time.sleep(2)

    def set_ac_averaging(self, naverages=10): # Set number of readings for the moving average filter
        '''Set the number of points to take for the moving average filter.'''
        self.ins.write(f'SENS:VOLT:AVER:COUN {naverages}')

    def set_delay(self,delay_time): # Set Trigger delay
        '''Set the trigger delay.'''
        self.ins.write(f'TRIG:DEL {delay_time}')

    def read(self): # Read instrument current value
        '''Return the current reading.'''
        self.ins.write('INIT:CONT ON')
        return float(self.ins.query('FETC?'))

    def slow_read(self): # Read instrument current value
        '''Deprecated method. Use read().'''
        self.ins.write('INIT:CONT ON')
        time.sleep(20)
        reading = self.ins.query('FETC?')
        time.sleep(20)
        return float(reading)

class Keithley2001(Keithley2015,Init): # Digital Multimeter

    def set_to_acv(self, vrange='AUTO',speed='MED', detector='RMS'): # Set instrument to ACV      
        '''Set the unit to measure AC Voltage.''' 
        self.ins.write('SENS:FUNC "VOLT:AC"')
        # Avaliable modes | RMS, AVERage, LFRMs, NPeak, PPeak
        self.ins.write(f'SENS:VOLT:AC:DET:FUNC {detector}')

        if vrange == 'AUTO':
            self.ins.write('SENS:VOLT:AC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:VOLT:AC:RANG {vrange}')


    def set_to_thermocouple(self,tctype='J'): # Set instrument to Thermocouple
        '''Set the unit to measure T/C temperature.'''
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write('SENS:TEMP:TRAN TC')
        self.ins.write(f'SENS:TEMP:TC:TYPE {tctype}')

    def set_to_4wire_rtd(self, rtdtype='PT385'): # Set instrument to 4-Wire RTD
        '''Set the unit to measure 4-Wire RTD Temperature.'''
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write('SENS:TEMP:TRAN FRTD')
        self.ins.write(f'SENS:TEMP:RTD:TYPE {rtdtype}')

    def set_to_2wire_rtd(self, rtdtype='PT385'): # Set instrument to 3-Wire RTD
        '''Set the unit to measure 2-Wire RTD temperature.'''
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write('SENS:TEMP:TRAN RTD')
        self.ins.write(f'SENS:TEMP:RTD:TYPE {rtdtype}')
        time.sleep(2)

    def read(self): # Read instrument current value
        '''Take the current measurement.'''
        self.ins.write('INIT:CONT ON')
        result_string = self.ins.query('FETC?')
        msmnt = re.search('\S+[Ee][+-]?\d\d', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)

    def slow_read(self): # Read slower filter results
        '''Deprecated. Use read().'''
        self.ins.write('INIT:CONT ON')
        time.sleep(20)
        result_string = self.ins.query('FETC?')
        msmnt = re.search('\S+[Ee][+-]?\d\d', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)

class HP3458A(Init): # Reference Multimeter

    '''HP 3458 Reference Multimeter.'''

    def __init__(self,resource_address): # Allow GPIB reading in ASCII format
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.write('END ALWAYS')
        self.ins.write('OFORMAT ASCII')
        self.ins.timeout = 60e3

    def auto_cal(self): # Auto Calibration
        '''Auto cal the unit.'''
        self.ins.write('ACAL')

    def nplc(self,nplc): # Set number of power line cycles per reading
        '''Set the number of power line cycles per reading.'''
        self.ins.write(f'NPLC {nplc}')    

    def set_to_dcv(self, vrange='AUTO', nplc=100): # Set to DCV
        '''Set the unit to read DC Voltage.'''
        self.ins.write(f'DCV,{vrange} ; NPLC {nplc}; TRIG AUTO')

    def set_to_acv(self, vrange='AUTO', nplc=100): # Set to ACV
        '''Set the unit to read AC Voltage.'''
        self.ins.write(f'ACV,{vrange} ; NPLC {nplc}; TRIG AUTO')

    def set_to_2wire_res(self, resrange='AUTO', nplc=100): # Set to 2-Wire Res
        '''Set the unit to read 2-Wire Resistance.'''
        self.ins.write(f'OHM,{resrange} ; NPLC {nplc}; TRIG AUTO')

    def set_to_4wire_res(self, resrange='AUTO', nplc=100): # Set to 4-Wire Res
        '''Set the unit to read 4-Wire Resistance.'''
        self.ins.write(f'OHMF,{resrange} ; NPLC {nplc}; TRIG AUTO')

    def set_to_dci(self, irange='AUTO', nplc=100): # Set to DCI
        '''Set the unit to read DC Current.'''
        self.ins.write(f'DCI,{irange} ; NPLC {nplc}; TRIG AUTO')

    def set_to_aci(self, irange='AUTO', nplc=100): # Set to ACI
        '''Set the unit to read AC Current.'''
        self.ins.write(f'ACI,{irange} ; NPLC {nplc}; TRIG AUTO')

    def set_trig_delay(self,delay):
        '''Set the unit trigger delay.'''
        self.ins.write(f'DELAY {delay}')

    def msg(self,string): # Send a message to the display
        '''Display a message on the unit display.'''
        self.ins.write(f'DISP MSG "{string}"')

    def get_display(self): # Get current display
        '''Get the current characters on the unit display.'''
        return self.ins.query('DSP?')

    def read(self): # Read Current Value
        '''Return the current measurement.'''
        return float(self.ins.query('SPOLL?'))               

class RSFSP(Init): # Spectrum Analyzer

    '''Rohde & Schwarz FSP Series Spectrum Analyzer'''

    def __init__(self,resource_address): # Initialize instrument through PyVisa
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.timeout = 300e3
        self.ins.write('*RST')
        self.ins.write('SYST:DISP:UPD ON') # Allows the display to update

    def clear_write_mode(self): # Set trace mode to clear/write
        '''Sets trace to clear/write mode.'''
        self.ins.write('DISP:WIND:TRAC:MODE WRIT')

    def input_attenuation(self,dB='AUTO'): # Set the input attentuation
        '''Sets the input attenuation.'''
        if dB == 'Auto':
            self.ins.write('INP:ATT:AUTO ON')
        else:
            self.ins.write(f'INP:ATT {dB}dB')

    def set_averaging(self,n): # Set trace mode to average
        '''Set trace averaging.'''
        self.ins.write(f'AVER:COUNT {n}; DISP:WIND:TRAC:MODE AVER; AVER:STAT ON; INIT; *WAI')

    def single_sweep(self): # Single sweep mode
        '''Set unit to single sweep mode.'''
        self.ins.write('INIT:CONT OFF')

    def center(self,frequency): # Set center frequency
        '''Set the unit center frequency.'''
        self.ins.write(f'FREQ:CENT {frequency}; *WAI')

    def start(self,frequency): # Set start frequency
        '''Set the unit start frequency.'''
        self.ins.write(f'FREQ:START {frequency}')

    def stop(self,frequency): # Set stop frequency
        '''Set the unit stop frequency.'''
        self.ins.write(f'FREQ:STOP {frequency}')

    def span(self,span): # Set span
        '''Set the unit frequency span.'''
        if span == 'Full':
            self.ins.write('FREQ:SPAN:FULL')
        elif span == 'Zero':
            self.ins.write('FREQ:SPAN 0Hz')
        else:
            self.ins.write(f'FREQ:SPAN {span}')

    def rbw(self,bandwidth): # Set Resolution Bandwidth (decouples from VBW)
        '''Set the unit resolution bandwidth.'''
        self.ins.write(f'BAND {bandwidth}; *WAI')

    def vbw(self, bandwidth): # Set Video Bandwidth (decouples from RBW)
        '''Set the unit video bandwidth.'''
        self.ins.write(f'BAND:VID {bandwidth}; *WAI')

    def window(self,span, center, rbw, ref_level): # Set general measurement parameters
        '''Set the display window to given spectral parameters.'''
        self.span(span)
        self.center(center)
        self.rbw(rbw)
        self.set_ref_level(ref_level)
        time.sleep(0.5)

    def set_detector(self, dettype='SAMP'): # Set detector type
        '''Set unit detector type. (Valid types are APE, POS, NEG, AVER, RMS, SAMP, QPE)'''
        # Valid types are APE, POS, NEG, AVER, RMS, SAMP, QPE
        self.ins.write(f'DET {dettype}')

    def set_ref_level(self,level): # Set amplitude reference level
        '''Set the unit reference level.'''
        self.ins.write(f'DISP:WIND:TRAC:Y:RLEV {level}dBm; *WAI')

    def set_marker_freq(self,frequency): # Set marker frequency
        '''Set the unit marker frequency.'''
        self.ins.write(f'CALC:MARK ON; CALC:MARK:X {frequency}')

    def get_marker_power(self): # Grab Current marker reading
        '''Get the level reading of the current marker.'''
        return float(self.ins.query('CALC:MARK:Y?'))

    def ref_to_marker(self): # Set reference level to marker level
        '''Set the unit reference level to the current marker value.'''
        self.ins.write('CALC:MARK:FUNC:REF')

    def get_peak_power(self): # Set marker to peak and grab reading
        '''Get the peak power in the window.'''
        time.sleep(0.5)
        self.ins.write('CALC:MARK:MAX')
        return float(self.ins.query('CALC:MARK:Y?'))

    def get_thd(self): # Set to measure harmonics and grab THD
        '''Get THD of a given measurement. Requires proper firmware package for Harmonic Dist measurement.'''
        # DOes not work on FSP3
        self.ins.write('CALC:MARK:FUNC:HARM:STAT ON')
        self.ins.write('INIT:CONT ON; *WAI')
        return self.ins.query('CALC:MARK:FUNC:HARM:DIST?')

    def manual_harmonics(self,fund_freq, fund_power, n_harmonics): # Get worst harmonic distortion measurement
        '''Measure harmonics manually, returning the worst of n harmonic measurements.'''
        harmonics = []

        self.window(10e3,fund_freq,100, fund_power+1)

        time.sleep(float(self.ins.query('SWE:TIME?'))+0.5)
        carrier_power = float(self.get_peak_power())

        for i in range(0,n_harmonics):
            if fund_freq <= 100:
                self.window(50,(i+2)*fund_freq,10,fund_power+1)
            elif fund_freq < 5000:
                self.window(1000,(i+2)*fund_freq,100,fund_power+1)
            else:
                self.window(10e3,(i+2)*fund_freq,100,fund_power+1)

            time.sleep(float(self.ins.query('SWE:TIME?'))+0.5)
            harmonics.append(carrier_power - float(self.get_peak_power()))

        return -min(harmonics)

    def next_peak(self): # Move the marker to the next highest peak
        '''Move the marker to the next peak.'''
        self.ins.write('CALC:MARK:MAX:NEXT')

class HP53132A(Init): # Counter

    '''HP 53132A Frequency Counter.'''

    def input_coupling(self,channel=1, ctype='AC'): # Set input coupling mode
        '''Set the unit input coupling type.'''
        self.ins.write(f'INP{channel}:COUP {ctype}')

    def input_impedance(self,channel=1,impedance=1e6): # Set input impedance
        '''Set the unit input impedance.'''
        self.ins.write(f'INP{channel}:IMP {impedance} OHM')

    def averaging(self, n=100, state=True): # Set averaging mode and count
        '''Set the unit to averaging mode and set number of samples.'''
        if state:
            self.ins.write('INIT:CONT OFF')
            self.ins.write(f'CALC3:AVER:COUN {n}')
            self.ins.write('CALC3:AVER:TYPE MEAN')
            self.ins.write('DISP:TEXT:FEED "CALC3"')
            self.ins.write('CALC3:AVER:STAT ON')
            self.ins.write('INIT:CONT ON')

        else:
            self.ins.write('CALC3:AVER:STAT OFF')

    def std_deviation(self, n=100, state=True): # Set standard deviation mode and count
        '''Set the unit to standard deviation mode, and set number of samples.'''
        if state:
            self.ins.write('INIT:CONT OFF')
            self.ins.write(f'CALC3:AVER:COUN {n}')
            self.ins.write('CALC3:AVER:TYPE SDEV')
            self.ins.write('DISP:TEXT:FEED "CALC3"')
            self.ins.write('CALC3:AVER:STAT ON')
            self.ins.write('INIT:CONT ON')

        else:
            self.ins.write('CALC3:AVER:STAT OFF')

    def low_pass_filter(self,channel=1,status=True): # 100 kHz low-pass filter
        '''Engage the 100 kHz Low-pass filter.'''
        if status:
            self.ins.write(f'INP{channel}:FILT ON')
        else:
            self.ins.write(f'INP{channel}:FILT OFF')

    def rel_trigger_level(self,channel=1,percent=50): # Trigger Percent adjustment
        '''Set the unit relative trigger level.'''
        self.ins.write(f'SENS:EVEN{channel}:LEV:REL {percent}')

    def frequency_mode(self, channel=1, gate=1): # Frequency Measurement
        '''Set the unit to measure frequency on a given channel with a given gate time.'''
        self.ins.write(f'SENS:FUNC:ON "FREQ {channel}"')
        self.ins.write('SENS:FREQ:ARM:SOUR IMM')
        self.ins.write(f'SENS:FREQ:ARM:STOP:TIM {gate}')
        self.ins.write('INIT:CONT ON')

    def rise_mode(self): # Rise Time Measurement
        '''Set the unit to measure rise time. (Channel 1 only.)'''
        self.ins.write('SENS:FUNC:ON ":RISE:TIME 1"')
        self.ins.write('INIT:CONT ON')

    def fall_mode(self): # Fall Time Measurement
        '''Set the unit to measure fall time. (Channel 1 only.)'''
        self.ins.write('SENS:FUNC:ON ":FALL:TIME 1"')
        self.ins.write('INIT:CONT ON')

    def period_mode(self,channel=1, gate=1): # Period Measurement
        '''Set the unit to measure period on a given channel with a given gate time.'''
        self.ins.write(f'SENS:FUNC "PERIOD {channel}"')
        self.ins.write('SENS:FREQ:ARM:SOUR IMM')
        self.ins.write(f'SENS:FREQ:ARM:STOP:TIM {gate}')
        self.ins.write('INIT:CONT ON')

    def time_of_flight(self): # Time of Flight Measurement
        '''Set the unit to measure time between channel 1 and 2 signals.'''
        self.ins.write('SENS:FUNC "TINT 1,2"')
        self.ins.write('INIT:CONT ON')

    def read(self): # Read instrument result
        '''Return the current measurement.'''
        return float(self.ins.query('FETC?'))

class HP8901B(Init): # Modulation Analyzer

    '''HP 8901B Modulation Analyzer 100 kHz to 1.3 GHz.'''

    def am(self): # Amplitude Modulation
        '''Set unit to measure amplitude modulation.'''
        self.ins.write('M1')
    
    def fm(self): # Frequency Modulation
        '''Set unit to measure frequency modulation.'''
        self.ins.write('M2')

    def phim(self): # Phase Modulation
        '''Set the unit to measure phase modulation.'''
        self.ins.write('M3')

    def rf(self): # RF Power
        '''Set the unit to measure RF power.'''
        self.ins.write('M4')

    def freq(self): # Frequency
        '''Set the unit to measure frequency.'''
        self.ins.write('M5')

    def audio_freq(self): # Audio Frequency
        '''Set the unit to measure frequency on the audio input.'''
        self.ins.write('S1')

    def audio_dist(self): # Audio Distortion
        '''Set the unit to measur distortion on the audio input.'''
        self.ins.write('S2')

    def peak_plus(self): # Peak+ Detector
        '''Set the detector to +Peak mode.'''
        self.ins.write('D1')

    def peak_minus(self): # Peak- Detector
        '''Set the detector to -Peak mode.'''
        self.ins.write('D2')

    def peak_hold(self): # Peak Hold Detector
        '''Set the detector to Peak hold mode.'''
        self.ins.write('D3')

    def average(self): # Average Detector
        '''Set the detector to average mode.'''
        self.ins.write('D4')

    def distn1khz(self): # 1 kHz Distortion Detection
        '''Set the unit to measure 1 kHz distortion.'''
        self.ins.write('D5')

    def dist400hz(self): # 400 Hz Distortion Detection
        '''Set the unit to measure 400 Hz distortion.'''
        self.ins.write('D6')

    def rms(self): # RMS Detector
        '''Set the detector to RMS mode.'''
        self.ins.write('D8')

    def peak_half(self): # ±Peak/2 Detector
        '''Set the detector to ±Peak/2 mode.'''
        self.ins.write('D9')

    def log(self): # Log Display
        '''Set the measurement units to logarithmic.'''
        self.ins.write('LG')

    def linear(self): # Linear Display
        '''Set the measurement units to linear.'''
        self.ins.write('LN')

    def ratio(self, state='ON'): # Ratio Settings
        '''Set the unit to ratio mode.'''
        if state == 'ON':
            self.ins.write('R1')
        else:
            self.ins.write('R0')

    def highpass_off(self): # Disable all highpass filters
        '''Disable all high-pass filters.'''
        self.ins.write('H0')

    def hp50Hz(self): # 50 Hz Highpass Filters
        '''Engage the 50 Hz high-pass filter.'''
        self.ins.write('H1')

    def hp300Hz(self): # 300 Hz Highpass Filter
        '''Engage the 300 Hz high-pass filter.'''
        self.ins.write('H2')

    def lowpass_off(self): # Disable all lowpass filters
        '''Disable all low-pass filters.'''
        self.ins.write('L0')

    def lp3kHz(self): # 3 kHz Lowpass Filter
        '''Engage 3 kHz low-pass fiter.'''
        self.ins.write('L1')

    def lp15kHz(self): # 15 kHz Lowpass Filter
        '''Engage 15 kHz low-pass filter.'''
        self.ins.write('L2')

    def lp20kHz(self): # >20 kHz Lowpass FIlter
        '''Engage > 20 kHz low-pass filter.'''
        self.ins.write('L3')

    def auto(self): # Auto Operation
        '''Set unit to auto operation.'''
        self.ins.write('AU')
    
    def inpfreq(self): # Input Frequency (MHz)
        '''Tune unit oscillator frequency to input frequency.'''
        self.ins.write('MZ')

    def am_cal(self): # AM Calibration Signal
        '''Set the unit to AM and engage the AM cal signal.'''
        self.ins.write('M1C1')

    def fm_cal(self): # FM Calibration Signal
        '''Set the unit to FM and engage the FM cal signal.'''
        self.ins.write('M2C1')

    def reset(self): # Reset Analyzer
        '''Clear the data lines.'''
        self.ins.write('DCL')

    def read(self): # Take a measurement
        '''Read from the instrument.'''
        return float(self.ins.read())

class TSG4104A(Init): # Signal Generator

    '''Tektronix TSG4104A DC to 4 GHz Signal Generator.'''

    def silence(self): # Reset the instrument
        '''Disable all outputs.'''
        self.ins.write('ENBL 0')
        self.ins.write('ENBR 0')
        
    def rf(self, amp, frequency, unit='dBM'): # RF Output Units = {RMS, dBM}
        '''Set unit to output RF at a given level and frequency.'''
        if frequency >= 62.5e6:
            self.ins.write('ENBL 0')
            self.ins.write(f'AMPR {amp} {unit}')
            self.ins.write(f'FREQ {frequency}')
            self.ins.write('ENBR 1')
        else:
            swap('\nLF Output engaged. Swap output.')
            self.ins.write('ENBL 0')
            self.ins.write(f'FREQ {frequency}')
            self.ins.write(f'AMPL {amp} {unit}')
            self.ins.write('ENBL 1')

    def lf(self, amp, frequency, unit='dBm'): # LF Output
        '''Set unit to output LF at a given level and frequency.'''
        if frequency <= 62.5e6: 
            self.ins.write('ENBL 0')
            self.ins.write(f'FREQ {frequency}')
            self.ins.write(f'AMPL {amp} {unit}')
            self.ins.write('ENBL 1')
        else:
            swap('\nRF Output engaged. Swap output.')
            self.ins.write('ENBL 0')
            self.ins.write(f'AMPR {amp} {unit}')
            self.ins.write(f'FREQ {frequency}')
            self.ins.write('ENBR 1')

class HP8903B(Init): # Audio Analyzer

    '''HP 8903B Audio Analyzer.'''

    def rms_detector(self): # RMS Detector
        '''Set the detector to RMS mode.'''
        self.ins.write('A0')

    def avg_detector(self): # Average Detector
        '''Set the detector to average mode.'''
        self.ins.write('A1')

    def auto_op(self): # Auto Operation
        '''Set the unit to auto operation mode.'''
        self.ins.write('AU')

    def log_units(self): # Logarithmic units
        '''Set the measurement display to logarithmic units.'''
        self.ins.write('LG')

    def linear_units(self): # Linear units
        '''Set the measurement display to linear units.'''
        self.ins.write('LN')

    def lowpass_off(self): # Low-pass filters off
        '''Disengage all low-pass filters.'''
        self.ins.write('L0')

    def lp30kHz(self): # 30 kHz low-pass filter
        '''Engage the 30 kHz low-pass filter.'''
        self.ins.write('L1')
    
    def lp80kHz(self): # 80 kHz low-pass filter
        '''Engage the 80 kHz low-pass filter.'''
        self.ins.write('L2')

    def highpass_off(self): # High-pass filters off
        '''Disengage all high-pass filters.'''
        self.ins.write('H0')

    def hp400Hz(self): # 400 Hz high-pass filter
        '''Engage the 400 Hz high-pass filter.'''
        self.ins.write('H1')

    def righthp(self): # Right high-pass filter
        '''Engage the right high-pass filter.'''
        self.ins.write('H2')

    def ac_level(self): # AC Level Measurement
        '''Set the unit to measure AC voltage level.'''
        self.ins.write('M1')

    def dc_level(self): # DC Level Measurement
        '''Set the unit to measure DC voltage level.'''
        self.ins.write('S1')

    def sinad(self): # SINAD Distortion measurment
        '''Set the unit to measure SINAD (distortion).'''
        self.ins.write('M2')

    def distortion(self): # Harmonic Distortion Measurement
        '''Set the unit to measure THD.'''
        self.ins.write('M3')

    def snr(self): # Signal-Noise Ratio Measurement
        '''Set the unit to measure signal to noise ratio.'''
        self.ins.write('S2')

    def ratio(self, state=True): # Ratio mode
        '''Set the measurement state to ratio mode.'''
        if state:
            self.ins.write('R1')
        else:
            self.ins.write('R0')

    def special(self,number): # Special functions
        '''Enters a given special function code. Ex: 12.0SP'''
        self.ins.write(f'{number}SP')

    def outp(self,amplitude, frequency, unit='VL'): # Output
        '''Engage the unit audio output.'''
        self.ins.write(f'AP{amplitude}{unit}FR{frequency}HZ')

    def read_right(self): # Read right display
        '''Read measurement from right display.'''
        return float(self.ins.query('RR'))

    def read_left(self): # Read left display
        '''Read measurement from left display.'''
        return float(self.ins.query('RL'))

    def reset(self): # Reset instrument to default settings
        '''Reset the instrument to default state.'''
        self.ins.write('41.0SP')

    
# DUT's
class AgilentN5181A(Init): # Signal generator

    '''Agilent N5181A 100 kHz to 6 GHz Signal Generator.'''

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)

    def rf_output(self,power,frequency): # RF Output
        '''Engage the unit RF output at a given level and frequency.'''
        self.ins.write('OUTP:STAT 0')
        self.ins.write(f'FREQ {frequency}')
        self.ins.write(f'POW:AMPL {power} dBm')
        self.ins.write('OUTP:STAT 1')
             
    def silence(self): # Turn off RF output
        '''Disable RF output.'''
        self.ins.write('OUTP:STAT 0')

class HP3325B(Init): # Signal Generator

    '''HP 3325B DC to 20 MHz Signal Generator.'''

    def command(self,command):
        '''Sends an arbitrary command to the unit.'''
        self.ins.write(command)

    def sine_output(self, level, frequency, offset, unit='VO'): # VO is pp. VR is rms
        '''Sets the unit to output a sine wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU1':
            self.ins.write('FU 1')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def square_output(self, level, frequency, offset, unit='VO'): # Square Wave output
        '''Sets the unit to output a square wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU2':
            self.ins.write('FU 2')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def triangle_output(self, level, frequency, offset, unit='VO'): # Triangle Wave output
        '''Sets the unit to output a triangle wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU3':
            self.ins.write('FU 3')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def pos_ramp_output(self, level, frequency, offset, unit='VO'): # Positive Ramp Wave output
        '''Sets the unit to output a positive ramp wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU4':
            self.ins.write('FU 4')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def neg_ramp_output(self, level, frequency, offset, unit='VO'): # Negative Ramp Wave output
        '''Sets the unit to output a negative ramp wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU5':
            self.ins.write('FU 5')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit}  OF{offset}VO')

    def dc_offset_only(self,offset): # DC Offset output
        '''Sets the unit to output a given DC offset.'''
        if self.ins.query('FU?') != 'FU0':
            self.ins.write('FU 0')
        self.ins.write(f'OF{offset}VO')

    def phase_mode(self, phase): # Phase Output
        '''Set the unit to phase shift the output.'''
        self.ins.write('MP1')
        self.ins.write(f'PH{phase}DE')

    def cont_sweep(self): # Continuous Sweep mode
        '''Set the unit to continuous sweep mode.'''
        self.ins.write('SC')

    def sweep_start_freq(self,frequency): # Sweep Start Frequency
        '''Set the sweep start frequency.'''
        self.ins.write(f'ST{frequency:.1f}HZ')

    def sweep_stop_freq(self,frequency): # Sweep Stop Frequency
        '''Set the sweep stop frequency.'''
        self.ins.write(f'SP{frequency:.1f}HZ')

    def sweep_marker(self,frequency):   # Sweep Marker Frequency
        '''Set the sweep marker frequency.'''
        self.ins.write(f'MF{frequency}HZ')

    def sweep_time(self, swtime): # Sweep Time
        '''Set the sweep time.'''
        self.ins.write(f'TI{swtime:.3f}SE')

    def silence(self): # Shhhhhh
        '''Set the unit to minimal output.'''
        self.sine_output(0.001,10e3,0)

class HP3325A(HP3325B): # Signal Generator

    '''HP 3325A 20 MHz Signal Generator.'''

    def sine_output(self, level, frequency, offset, unit='VO'): # VO is pp. VR is rms
        '''Sets the unit to output a sine wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU1':
            self.ins.write('FU1AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def square_output(self, level, frequency, offset, unit='VO'): # Square Wave output
        '''Sets the unit to output a square wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU2':
            self.ins.write('FU2AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def triangle_output(self, level, frequency, offset, unit='VO'): # Triangle Wave output
        '''Sets the unit to output a triangle wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU3':
            self.ins.write('FU3AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def pos_ramp_output(self, level, frequency, offset, unit='VO'): # Positive Ramp Wave output
        '''Sets the unit to output a positive ramp wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU4':
            self.ins.write('FU4AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def neg_ramp_output(self, level, frequency, offset, unit='VO'): # Negative Ramp Wave output
        '''Sets the unit to output a negative ramp wave at a given level and frequency.'''
        if self.ins.query('FU?') != 'FU5':
            self.ins.write('FU5AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def dc_offset_only(self,offset): # DC Offset 
        '''Sets the unit to output a DC Level.'''
        if self.ins.query('FU?') != 'FU0':
            self.ins.write('FU0AC')
        self.ins.write(f'OF{offset}VO')

    def silence(self): # Shhhhhhhhhh
        '''Sets the unit to minimum output.'''
        self.sine_output(0.001,10e3,0)

class HP3314A(Init): # Signal Generator

    '''HP 3314 Signal Generator.'''

    def sine_output(self, level, frequency, offset, unit='VO'): # VO is VPP
        '''Sets the unit to output a sine wave at a given level and frequency.'''
        self.ins.write('FU 1')
        self.ins.write(f'FR{frequency:.1f}HZOF{offset}VOAP{level}{unit}')

    def square_output(self, level, frequency, offset, unit='VO'): # VO is VPP
        '''Sets the unit to output a square wave at a given level and frequency.'''
        self.ins.write('FU 2')
        self.ins.write(f'FR{frequency:.1f}HZOF{offset}VOAP{level}{unit}')

    def triangle_output(self, level, frequency, offset, unit='VO'): # VO is VPP
        '''Sets the unit to output a triangle wave at a given level and frequency.'''
        self.ins.write('FU 3')
        self.ins.write(f'FR{frequency:.1f}HZOF{offset}VOAP{level}{unit}')

if __name__ == '__main__':

    swap('\nDocumentation coming soon!')
