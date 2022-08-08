##########################################################
#                                                        #
#                                                        #
#                  Keithley 2015 DMM                     #
#                                                        #
#                                                        #
#                                                        #
#                                                        #
##########################################################
from Routines.Core.Instruments import initialize_ins
import multimeter

class Keithley2015(multimeter): # Digital Multimeter

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