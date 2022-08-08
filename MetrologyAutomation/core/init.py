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
from datetime import datetime
import matplotlib.pyplot as plt

# Common Methods

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