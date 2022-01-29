import pyvisa as pv
import time, re
import pandas as pd

# Common Functions

def initialize_ins(name='{instrument name}'): # Initialize an instrument
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
    input('\nPress enter to continue. . .')

def clear(): # Clear terminal
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def swap(message): # Halt and message
    clear()
    print(f'\n{message}')
    pause()
    clear()

# Instrument Classes

# Standards
class Init(): # Initializer Parent Class

    def __init__(self,resource_address): # Initialize instrument through PyVisa
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.timeout = 60e3

    def command(self,string): # Send and arbitrary command
        self.ins.write(string)

    def query(self,string): # Send an arbitrary query
        return self.ins.query(string)

class Fluke96270A(Init): # RF Reference Source

    def set_outp_mode(self,mode): # Select head or microwave output
        clear()
        if mode.lower() == 'microwave':
            self.ins.write(':OUTP:ROUT MICR')
            print('\nOutput source set to Microwave')
            input('\nPress enter to continue. . .')
            clear()
        elif mode.lower() == 'head':
            self.ins.write(':OUTP:ROUT HEAD')
            print('\nOutput source set to Leveling Head')
            input('\nPress enter to continue. . .')
            clear()
        else:
            print('\nInvalid output mode passed. Please enter either "head" or "microwave".')

    def sine_output(self,carrier,power): # Sine wave output
        self.ins.write('OUTP OFF')
        self.ins.write('INST SINE')
        self.ins.write('UNIT:POW DBM')
        self.ins.write(f'FREQ {carrier}')
        self.ins.write(f'POW {power}')
        time.sleep(1)
        self.ins.write('OUTP ON')

    def amplitude_modulation(self,carrier,power,rate,depth): # AM Output      
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
        self.ins.write('OUTP OFF')

class Fluke9640A(Fluke96270A,Init): # RF Reference Source
    
    def set_outp_mode(self, *args, **kwargs): # Overwriting unused method
        # This unit only outputs via leveling head
        pass

class HP33120A(Init): # Signal Generator

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.write('*RST')
        self.ins.write('VOLT:UNIT DBM')
        self.ins.write('APPL:SIN 1e3,-20')

    def output_unit(self,unit='DBM'): # Options are VPP,VRMS, and DBM
        self.ins.write(f'VOLT:UNIT {unit}')

    def sine_output(self,level,freq): # Sine wave output
        self.ins.write(f'APPL:SIN {freq},{level}')

    def ramp_output(self,level,freq): # Triangle output
        self.ins.write(f'APPL:RAMP {freq},{level}')

    def square_output(self,level,freq): # Square wave
        self.ins.write(f'APPL:SQU {freq},{level}')

    def dc_output(self,voltage): # DC Output
        self.ins.write(f'APPL:DC {voltage}')

    def dc_offset(self,offset_voltage): # DC Offset
        self.ins.write(f'VOLT:OFFS {offset_voltage}')

class Fluke55XXA(Init): # Multifunction Calibrator

    def wave_shape(self,shape='SINE'): # Change AC Waveform Shape
        # Options | SINE, TRI, SQUARE, TRUNCS
        self.ins.write(f'WAVE {shape}')

    def voltage_dc(self,voltage): # DCV Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {voltage} V, 0 Hz')
        if voltage >= 33:
            self.ins.write('*CLS')
            if voltage >= 100:
                #input('\n! High Voltage Warning ! Press enter to continue. . .')
                pass
        self.ins.write('OPER')

    def voltage_ac(self,voltage,frequency): # ACV Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {voltage} V, {frequency} Hz')
        if voltage >= 33:
            self.ins.write('*CLS')
            if voltage >= 100:
                #input('\n! High Voltage Warning ! Press enter to continue. . .')
                pass
        self.ins.write('OPER')

    def current_dc(self, current): # DCI Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {current} A, 0 Hz')
        self.ins.write('OPER')

    def current_ac(self,current,frequency): # ACI Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {current} A, {frequency} Hz')
        self.ins.write('LCOMP ON')
        self.ins.write('OPER')

    def resistance_nocomp(self,resistance): # Resistance Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {resistance} OHM')
        self.ins.write('ZCOMP NONE')
        self.ins.write('OPER')

    def resistance_2wire(self,resistance): # 2-Wire Resistance Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {resistance} OHM')
        self.ins.write('ZCOMP WIRE2')
        self.ins.write('OPER')

    def resistance_4wire(self,resistance): # 4-Wire Resistance Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {resistance} OHM')
        self.ins.write('ZCOMP WIRE4')
        self.ins.write('OPER')

    def capacitance(self,cap): # Capacitance Output
        self.ins.write('STBY')
        self.ins.write(f'OUT {cap} F')
        self.ins.write('OPER')

    def thermocouple_temp(self,temp,unit='C',type='K'): # T/C Output
        self.ins.write('STBY')
        self.ins.write(f'TC_TYPE {type}')

        if unit=='F':
            self.ins.write(f'OUT {temp} FAR')
        else:
            self.ins.write(f'OUT {temp} CEL')

        
        self.ins.write('OPER')

    def rtd_2wire_simulation(self,temp,unit='C',type='PT385'): # 2-Wire RTD Output
        self.ins.write('STBY')

        if unit=='F':
            self.ins.write(f'OUT {temp} FAR')
        else:
            self.ins.write(f'OUT {temp} CEL')

        self.ins.write(f'RTD_TYPE {type}')
        self.ins.write('ZCOMP WIRE2')
        self.ins.write('OPER')

    def rtd_4wire_simulation(self,temp,unit='C',type='PT385'): # 4-Wire RTD Output
        self.ins.write('STBY')

        if unit=='F':
            self.ins.write(f'OUT {temp} FAR')
        else:
            self.ins.write(f'OUT {temp} CEL')

        self.ins.write(f'RTD_TYPE {type}')
        self.ins.write('ZCOMP WIRE4')
        self.ins.write('OPER')

    def silence(self): # Shhhhhhhhhhhh
            self.ins.write('STBY')
            time.sleep(0.5)

class HP4418B(Init): # RF Power Meter

    def clear_errors(self): # Clear error register
        self.ins.write('*CLS')

    def set_unit(self, unit='DBM'): # Set output unit
        # Options | W or DBM
        self.ins.write(f'UNIT1:POW {unit}')

    def zero_sensor(self): # Zero power sensor
        clear()
        input('\nEnsure power sensor is disconnected. Press enter to continue. . .')
        print('\nZeroing the power sensor. . .')
        self.ins.write('CAL1:ZERO:AUTO ONCE')
        time.sleep(10)
        input('\nSensor zeroed. Press enter to continue. . .')
        clear()
    
    def cal_sensor(self): # Calibrate Power Sensor
        clear()
        input('\nConnect power sensor to calibration output. Press enter to continue. . .')
        print('\nCalibrating sensor. . .')
        self.ins.write('CAL1:AUTO ONCE')
        time.sleep(10)
        input('\nCalibration complete. Press enter to continue. . .')
        clear()

    def measure_power(self, freq, model='HP8482A'): # Measure power w/internal corrections
        self.ins.write('ABORt1')
        self.ins.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.ins.write(f'SENS1:CORR:CSET1:SEL "{model}"')
        self.ins.write('SENS1:CORR:CSET1:STAT ON')
        self.ins.write('SENSe1:FREQuency {:.6f}'.format(freq))
        self.ins.write('INIT1')
        time.sleep(3)     
        return float(self.ins.query('FETC1?'))

    def measure_power_w_corrections(self,correction): # Measure power with given corrections
        self.ins.write('ABORt1')
        self.ins.write('CONFigure1:POWer:AC DEF,4,(@1)')
        self.ins.write(f'CAL1:RCF {correction:.2f}PCT')
        self.ins.write('INIT1')
        time.sleep(5)
        self.ins.write('FETC1?')
        time.sleep(3)
        return float(self.ins.read())

    def load_corrections(self,inlist): # Load correction factors
        from scipy.interpolate import interp1d
        df = pd.read_csv(inlist)
        corr_freqs = [float(a)*1e6 for a in df['Frequency']]
        corr_factors = [float(a) for a in df['Factor']]   
        return interp1d(corr_freqs, corr_factors, kind='cubic')

class Keithley2015(Init): # Digital Multimeter

    def stealth(self,status='OFF'): # Disable the display
        self.ins.write(f'DISP:ENAB {status}')

    def set_to_dcv(self, range='AUTO',speed='MED'): # Set instrument to DCV      
        self.ins.write('SENS:FUNC "VOLT:DC"')
        #self.ins.write('INIT:CONT ON')

        if range == 'AUTO':
            self.ins.write('SENS:VOLT:DC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:VOLT:DC:RANG {range}')

        if speed == 'MED':
            self.ins.write('SENS:VOLT:DC:NPLC 1')
        elif speed == 'SLOW':
            self.ins.write('SENS:VOLT:DC:NPLC 10')
        else:
            self.ins.write('SENS:VOLT:DC:NPLC 0.1')

        time.sleep(2)

    def set_to_acv(self, range='AUTO',speed='MED'): # Set instrument to ACV       
        self.ins.write('SENS:FUNC "VOLT:AC"')
        self.ins.write('UNIT:VOLT:AC V')

        if range == 'AUTO':
            self.ins.write('SENS:VOLT:AC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:VOLT:AC:RANG {range}')

        # Figure out how to change the rate on ACV mode
        time.sleep(2)

    def set_to_dbm(self, impedance=50):
        self.set_to_acv()
        self.ins.write(f'UNIT:VOLT:AC:DBM:IMP {impedance}')
        self.ins.write('UNIT:VOLT:AC DBM')

    def set_to_THD(self, frequency, unit='dB'):
        if unit == '%':
            self.ins.write('SENS:FUNC "DIST"')
            self.ins.write(f'SENS:DIST:FREQ {frequency}')
        else:
            self.ins.write('SENS:FUNC "DIST"')
            self.ins.write('SENS:DIST:TYPE SINAD')
            self.ins.write('SENS:DIST:TYPE THD')
            self.ins.write(f'SENS:DIST:FREQ {frequency}')

    def thd_freq(self,frequency):
        self.ins.write(f'SENS:DIST:FREQ {frequency}')

    def set_to_2wire_res(self, range='AUTO', speed='MED'): # Set instrument to 2 Wire Resistance
        self.ins.write('SENS:FUNC "RES"')

        if range == 'AUTO':
            self.ins.write('SENS:RES:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:RES:RANG {range}')
        time.sleep(2)

    def set_to_4wire_res(self, range='AUTO', speed='MED'): # Set instrument to 4 Wire Resistance
        self.ins.write('SENS:FUNC "FRES"')

        if range == 'AUTO':
            self.ins.write('SENS:FRES:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:FRES:RANG {range}')
        time.sleep(2)

    def set_to_aci(self, range='AUTO', speed='MED'): # Set instrument to ACI
        self.ins.write('SENS:FUNC "CURR:AC"')
        #self.ins.write('INIT:CONT ON')

        if range == 'AUTO':
            self.ins.write('SENS:CURR:AC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:CURR:AC:RANG {range}')

        # Figure out how to change the rate on ACImode
        time.sleep(2)

    def set_to_dci(self, range='AUTO', speed='MED'): # Set instrument to DCI
        self.ins.write('SENS:FUNC "CURR:DC"')

        if range == 'AUTO':
            self.ins.write('SENS:CURR:DC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:CURR:DC:RANG {range}')
        time.sleep(2)

    def set_to_freq(self): # Set instrument to Frequency
        self.ins.write('SENS:FUNC "FREQ"')
        time.sleep(2)

    def set_to_thermocouple(self,type='J'): # Set instrument to Thermocouple
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write(f'SENS:TEMP:TC:TYPE {type}')
        time.sleep(2)

    def set_ac_averaging(self, naverages=10): # Set number of readings for the moving average filter
        self.ins.write(f'SENS:VOLT:AVER:COUN {naverages}')

    def set_delay(self,delay_time): # Set Trigger delay
        self.ins.write(f'TRIG:DEL {delay_time}')

    def read(self): # Read instrument current value
        self.ins.write('INIT:CONT ON')
        return float(self.ins.query('FETC?'))

    def slow_read(self): # Read instrument current value
        self.ins.write('INIT:CONT ON')
        time.sleep(20)
        reading = self.ins.query('FETC?')
        time.sleep(20)
        return float(reading)

class Keithley2001(Keithley2015,Init): # Digital Multimeter

    def set_to_acv(self, range='AUTO',speed='MED', detector='RMS'): # Set instrument to ACV       
        self.ins.write('SENS:FUNC "VOLT:AC"')
        # Avaliable modes | RMS, AVERage, LFRMs, NPeak, PPeak
        self.ins.write(f'SENS:VOLT:AC:DET:FUNC {detector}')

        if range == 'AUTO':
            self.ins.write('SENS:VOLT:AC:RANG:AUTO 1')
        else:
            self.ins.write(f'SENS:VOLT:AC:RANG {range}')

        # Figure out how to change the rate on ACV mode
        time.sleep(2)

    def set_to_thermocouple(self,type='J'): # Set instrument to Thermocouple
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write('SENS:TEMP:TRAN TC')
        self.ins.write(f'SENS:TEMP:TC:TYPE {type}')
        time.sleep(2)

    def set_to_4wire_rtd(self, type='PT385'): # Set instrument to 4-Wire RTD
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write('SENS:TEMP:TRAN FRTD')
        self.ins.write(f'SENS:TEMP:RTD:TYPE {type}')
        time.sleep(2)

    def set_to_2wire_rtd(self, type='PT385'): # Set instrument to 3-Wire RTD
        self.ins.write('SENS:FUNC "TEMP"')
        self.ins.write('SENS:TEMP:TRAN RTD')
        self.ins.write(f'SENS:TEMP:RTD:TYPE {type}')
        time.sleep(2)

    def read(self): # Read instrument current value
        self.ins.write('INIT:CONT ON')
        result_string = self.ins.query('FETC?')
        msmnt = re.search('\S+[Ee][+-]?\d\d', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)

    def slow_read(self): # Read slower filter results
        self.ins.write('INIT:CONT ON')
        time.sleep(20)
        result_string = self.ins.query('FETC?')
        msmnt = re.search('\S+[Ee][+-]?\d\d', result_string).group(0) # Regex search to grab +/-XXx.XXXX+/-EXX
        return float(msmnt)

class HP3458A(Init): # Reference Multimeter

    def __init__(self,resource_address): # Allow GPIB reading in ASCII format
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.write('END ALWAYS')
        self.ins.write('OFORMAT ASCII')
        self.ins.timeout = 60e3

    def auto_cal(self): # Auto Calibration
        self.ins.write('ACAL')

    def nplc(self,nplc): # Set number of power line cycles per reading
        self.ins.write(f'NPLC {nplc}')    

    def set_to_dcv(self, range='AUTO', nplc=100): # Set to DCV
        self.ins.write(f'DCV,{range} ; NPLC {nplc}; TRIG AUTO')

    def set_to_acv(self, range='AUTO', nplc=100): # Set to ACV
        self.ins.write(f'ACV,{range} ; NPLC {nplc}; TRIG AUTO')

    def set_to_2wire_res(self, range='AUTO', nplc=100): # Set to 2-Wire Res
        self.ins.write(f'OHM,{range} ; NPLC {nplc}; TRIG AUTO')

    def set_to_4wire_res(self, range='AUTO', nplc=100): # Set to 4-Wire Res
        self.ins.write(f'OHMF,{range} ; NPLC {nplc}; TRIG AUTO')

    def set_to_dci(self, range='AUTO', nplc=100): # Set to DCI
        self.ins.write(f'DCI,{range} ; NPLC {nplc}; TRIG AUTO')

    def set_to_aci(self, range='AUTO', nplc=100): # Set to ACI
        self.ins.write(f'ACI,{range} ; NPLC {nplc}; TRIG AUTO')

    def set_trig_delay(self,delay):
        self.ins.write(f'DELAY {delay}')

    def msg(self,string): # Send a message to the display
        self.ins.write(f'DISP MSG "{string}"')

    def get_display(self): # Get current display
        return self.ins.query('DSP?')

    def read(self): # Read Current Value
        return float(self.ins.query('SPOLL?'))               

class RSFSP(Init): # Spectrum Analyzer

    def __init__(self,resource_address): # Initialize instrument through PyVisa
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)
        self.ins.timeout = 300e3
        self.ins.write('*RST')
        self.ins.write('SYST:DISP:UPD ON') # Allows the display to update

    def clear_write_mode(self): # Set trace mode to clear/write
        self.ins.write('DISP:WIND:TRAC:MODE WRIT')

    def input_attenuation(self,dB='AUTO'): # Set the input attentuation
        if dB == 'Auto':
            self.ins.write('INP:ATT:AUTO ON')
        else:
            self.ins.write(f'INP:ATT {dB}dB')

    def set_averaging(self,n): # Set trace mode to average
        self.ins.write(f'AVER:COUNT {n}; DISP:WIND:TRAC:MODE AVER; AVER:STAT ON; INIT; *WAI')

    def single_sweep(self): # Single sweep mode
        self.ins.write('INIT:CONT OFF')

    def center(self,frequency): # Set center frequency
        self.ins.write(f'FREQ:CENT {frequency}; *WAI')

    def start(self,frequency): # Set start frequency
        self.ins.write(f'FREQ:START {frequency}')

    def stop(self,frequency): # Set stop frequency
        self.ins.write(f'FREQ:STOP {frequency}')

    def span(self,span): # Set span
        if span == 'Full':
            self.ins.write('FREQ:SPAN:FULL')
        elif span == 'Zero':
            self.ins.write('FREQ:SPAN 0Hz')
        else:
            self.ins.write(f'FREQ:SPAN {span}')

    def rbw(self,bandwidth): # Set Resolution Bandwidth (decouples from VBW)
        self.ins.write(f'BAND {bandwidth}; *WAI')

    def vbw(self, bandwidth): # Set Video Bandwidth (decouples from RBW)
        self.ins.write(f'BAND:VID {bandwidth}; *WAI')

    def window(self,span, center, rbw, ref_level): # Set general measurement parameters
        self.span(span)
        self.center(center)
        self.rbw(rbw)
        self.set_ref_level(ref_level)
        time.sleep(0.5)

    def set_detector(self, type='SAMP'): # Set detector type
        # Valid types are APE, POS, NEG, AVER, RMS, SAMP, QPE
        self.ins.write(f'DET {type}')

    def set_ref_level(self,level): # Set amplitude reference level
        self.ins.write(f'DISP:WIND:TRAC:Y:RLEV {level}dBm; *WAI')

    def set_marker_freq(self,frequency): # Set marker frequency
        self.ins.write(f'CALC:MARK ON; CALC:MARK:X {frequency}')

    def get_marker_power(self): # Grab Current marker reading
        return float(self.ins.query('CALC:MARK:Y?'))

    def ref_to_marker(self): # Set reference level to marker level
        self.ins.write('CALC:MARK:FUNC:REF')

    def get_peak_power(self): # Set marker to peak and grab reading
        time.sleep(0.5)
        self.ins.write('CALC:MARK:MAX')
        return float(self.ins.query('CALC:MARK:Y?'))

    def get_thd(self): # Set to measure harmonics and grab THD
        # DOes not work on FSP3
        self.ins.write('CALC:MARK:FUNC:HARM:STAT ON')
        self.write('INIT:CONT ON; *WAI')
        return self.ins.query('CALC:MARK:FUNC:HARM:DIST?')

    def manual_harmonics(self,fund_freq, fund_power, n_harmonics): # Get worst harmonic distortion
        harmonics = []

        self.window(10e3,fund_freq,100, fund_power+1)

        time.sleep(float(self.ins.query('SWE:TIME?'))+0.5)
        carrier_power = float(self.get_peak_power())

        for i in range(0,n_harmonics):
            if fund_freq <= 100:
                self.window(50,(i+2)*fund_freq,10,fund_power-20)
            elif fund_freq < 5000:
                self.window(1000,(i+2)*fund_freq,100,fund_power-20 )
            else:
                self.window(10e3,(i+2)*fund_freq,100,fund_power-20)

            time.sleep(float(self.ins.query('SWE:TIME?'))+0.5)
            harmonics.append(carrier_power - float(self.get_peak_power()))

        return -min(harmonics)

    def next_peak(self): # Move the marker to the next highest peak
        self.ins.write('CALC:MARK:MAX:NEXT')

class HP53132A(Init): # Counter

    def input_coupling(self,channel=1, type='AC'):
        self.ins.write(f'INP{channel}:COUP {type}')

    def input_impedance(self,channel=1,impedance=1e6):
        self.ins.write(f'INP{channel}:IMP {impedance} OHM')

    def averaging(self, n=100, state=True):
        if state:
            self.ins.write('INIT:CONT OFF')
            self.ins.write(f'CALC3:AVER:COUN {n}')
            self.ins.write('CALC3:AVER:TYPE MEAN')
            self.ins.write('DISP:TEXT:FEED "CALC3"')
            self.ins.write('CALC3:AVER:STAT ON')
            self.ins.write('INIT:CONT ON')

        else:
            self.ins.write('CALC3:AVER:STAT OFF')

    def std_deviation(self, n=100, state=True):
        if state:
            self.ins.write('INIT:CONT OFF')
            self.ins.write(f'CALC3:AVER:COUN {n}')
            self.ins.write('CALC3:AVER:TYPE SDEV')
            self.ins.write('DISP:TEXT:FEED "CALC3"')
            self.ins.write('CALC3:AVER:STAT ON')
            self.ins.write('INIT:CONT ON')

        else:
            self.ins.write('CALC3:AVER:STAT OFF')

    def low_pass_filter(self,channel=1,status=True):

        if status:
            self.ins.write(f'INP{channel}:FILT ON')
        else:
            self.ins.write(f'INP{channel}:FILT OFF')

    def rel_trigger_level(self,channel=1,percent=50):
        self.ins.write(f'SENS:EVEN{channel}:LEV:REL {percent}')

    def frequency_mode(self, channel=1, gate=1):
        self.ins.write(f'SENS:FUNC:ON "FREQ {channel}"')
        self.ins.write('SENS:FREQ:ARM:SOUR IMM')
        self.ins.write(f'SENS:FREQ:ARM:STOP:TIM {gate}')
        self.ins.write('INIT:CONT ON')

    def rise_mode(self):
        self.ins.write(f'SENS:FUNC:ON ":RISE:TIME 1"')
        self.ins.write('INIT:CONT ON')

    def fall_mode(self):
        self.ins.write('SENS:FUNC:ON ":FALL:TIME 1"')
        self.ins.write('INIT:CONT ON')

    def period_mode(self,channel=1, gate=1):
        self.ins.write(f'SENS:FUNC "PERIOD {channel}"')
        self.ins.write('SENS:FREQ:ARM:SOUR IMM')
        self.ins.write(f'SENS:FREQ:ARM:STOP:TIM {gate}')
        self.ins.write('INIT:CONT ON')

    def time_of_flight(self):
        self.ins.write('SENS:FUNC "TINT 1,2"')
        self.ins.write('INIT:CONT ON')

    def read(self):
        return float(self.ins.query('FETC?'))

class HP8901B(Init): # Modulation Analyzer

    def am(self): # Amplitude Modulation
        self.ins.write('M1')
    
    def fm(self): # Frequency Modulation
        self.ins.write('M2')

    def phim(self): # Phase Modulation
        self.ins.write('M3')

    def rf(self): # RF Power
        self.ins.write('M4')

    def freq(self): # Frequency
        self.ins.write('M5')

    def audio_freq(self): # Audio Frequency
        self.ins.write('S1')

    def audio_dist(self): # Audio Distortion
        self.ins.write('S2')

    def peak_plus(self): # Peak+ Detector
        self.ins.write('D1')

    def peak_minus(self): # Peak- Detector
        self.ins.write('D2')

    def peak_hold(self): # Peak Hold Detector
        self.ins.write('D3')

    def average(self): # Average Detector
        self.ins.write('D4')

    def distn1khz(self): # 1 kHz Distortion Detection
        self.ins.write('D5')

    def dist400hz(self): # 400 Hz Distortion Detection
        self.ins.write('D6')

    def rms(self): # RMS Detector
        self.ins.write('D8')

    def peak_half(self): # ±Peak/2 Detector
        self.ins.write('D9')

    def log(self): # Log Display
        self.ins.write('LG')

    def linear(self): # Linear Display
        self.ins.write('LN')

    def ratio(self, state='ON'): # Ratio Settings
        if state == 'ON':
            self.ins.write('R1')
        else:
            self.ins.write('R0')

    def highpass_off(self): # Disable all highpass filters
        self.ins.write('H0')

    def hp50Hz(self): # 50 Hz Highpass Filters
        self.ins.write('H1')

    def hp300Hz(self): # 300 Hz Highpass Filter
        self.ins.write('H2')

    def lowpass_off(self): # Disable all lowpass filters
        self.ins.write('L0')

    def lp3kHz(self): # 3 kHz Lowpass Filter
        self.ins.write('L1')

    def lp15kHz(self): # 15 kHz Lowpass Filter
        self.ins.write('L2')

    def lp20khz(self): # >20 kHz Lowpass FIlter
        self.ins.write('L3')

    def auto(self): # Auto Operation
        self.ins.write('AU')
    
    def inpfreq(self): # Input Frequency (MHz)
        self.ins.write('MZ')

    def am_cal(self): # AM Calibration Signal
        self.ins.write('13.0SP')

    def fm_cal(self): # FM Calibration Signal
        self.ins.write('12.0SP')

    def reset(self): # Reset Analyzer
        self.ins.write('DCL')

    def read(self): # Take a measurement
        return float(self.ins.query('GET'))

class TSG4104A(Init): # Signal Generator

    def silence(self): # Reset the instrument
        self.ins.write('ENBL 0')
        self.ins.write('ENBR 0')
        
    def rf(self, amp, frequency, unit='dBM'): # RF Output Units = {RMS, dBM}
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

# DUT's
class AgilentN5181A(Init): # Signal generator

    def __init__(self,resource_address):
        rm = pv.ResourceManager()
        self.ins = rm.open_resource(resource_address)

    def rf_output(self,power,frequency): # RF Output
        self.ins.write('OUTP:STAT 0')
        self.ins.write(f'FREQ {frequency}')
        self.ins.write(f'POW:AMPL {power} dBm')
        self.ins.write(f'OUTP:STAT 1')
        time.sleep(3)
             
    def silence(self): # Turn off RF output
        self.ins.write('OUTP:STAT 0')

class HP3325B(Init): # Signal Generator

    def command(self,command):
        self.ins.write(command)

    def sine_output(self, level, frequency, offset, unit='VO'): # VO is pp. VR is rms
        if self.ins.query('FU?') != 'FU1':
            self.ins.write('FU 1')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def square_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU2':
            self.ins.write('FU 2')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def triangle_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU3':
            self.ins.write('FU 3')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def pos_ramp_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU4':
            self.ins.write('FU 4')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit} OF{offset}VO')

    def neg_ramp_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU5':
            self.ins.write('FU 5')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZ AM{level}{unit}  OF{offset}VO')

    def dc_offset_only(self,offset):
        if self.ins.query('FU?') != 'FU0':
            self.ins.write('FU 0')
        self.ins.write(f'OF{offset}VO')

    def phase_mode(self, phase):
        self.ins.write('MP1')
        self.ins.write(f'PH{phase}DE')

    def cont_sweep(self):
        self.ins.write('SC')

    def sweep_start_freq(self,frequency):
        self.ins.write(f'ST{frequency:.1f}HZ')

    def sweep_stop_freq(self,frequency):
        self.ins.write(f'SP{frequency:.1f}HZ')

    def sweep_marker(self,frequency):
        self.ins.write(f'MF{frequency}HZ')

    def sweep_time(self, time):
        self.ins.write(f'TI{time:.3f}SE')

    def silence(self):
        self.sine_output(0.001,10e3,0)

class HP3325A(HP3325B): # Signal Generator

    def sine_output(self, level, frequency, offset, unit='VO'): # VO is pp. VR is rms
        if self.ins.query('FU?') != 'FU1':
            self.ins.write('FU1AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def square_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU2':
            self.ins.write('FU2AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def triangle_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU3':
            self.ins.write('FU3AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def pos_ramp_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU4':
            self.ins.write('FU4AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def neg_ramp_output(self, level, frequency, offset, unit='VO'):
        if self.ins.query('FU?') != 'FU5':
            self.ins.write('FU5AC')
        self.ins.write('OF0.0VO')
        self.ins.write(f'FR{frequency:.1f}HZAM{level}{unit}OF{offset}VO')

    def dc_offset_only(self,offset):
        if self.ins.query('FU?') != 'FU0':
            self.ins.write('FU0AC')
        self.ins.write(f'OF{offset}VO')

    def silence(self):
        self.sine_output(0.001,10e3,0)

class HP3314A(Init): # Signal Generator

    def sine_output(self, level, frequency, offset, unit='VO'): # VO is VPP
        self.ins.write('FU 1')
        self.ins.write(f'FR{frequency:.1f}HZOF{offset}VOAP{level}{unit}')

    def square_output(self, level, frequency, offset, unit='VO'): # VO is VPP
        self.ins.write('FU 2')
        self.ins.write(f'FR{frequency:.1f}HZOF{offset}VOAP{level}{unit}')

    def triangle_output(self, level, frequency, offset, unit='VO'): # VO is VPP
        self.ins.write('FU 3')
        self.ins.write(f'FR{frequency:.1f}HZOF{offset}VOAP{level}{unit}')

if __name__ == '__main__':

    swap('\nDocumentation coming soon!')
