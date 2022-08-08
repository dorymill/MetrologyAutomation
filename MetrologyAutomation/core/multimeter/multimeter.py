##########################################################
#                                                        #
#                                                        #
#            Digital Multimeter Interface                #
#                                                        #
#                                                        #
#                                                        #
#                                                        #
##########################################################
from abc import ABC, abstractmethod, abstractproperty
import sys
sys.path.append('../core')

from core.init import *

class Multimeter(ABC, Init):

    @abstractmethod
    def set_to_dcv(self, speed='AUTO', vrange='AUTO'):
        pass

    @abstractmethod
    def set_to_acv(self, aperature='AUTO', vrange='AUTO'):
        pass

    @abstractmethod
    def set_to_2wire_res(self, resrange='AUTO', speed='MED'):
        pass

    @abstractmethod
    def set_to_4wire_res(self, resrange='AUTO', speed='MED'):
        pass

    @abstractmethod
    def set_to_aci(self, irange='AUTO', speed='MED'):
        pass

    @abstractmethod
    def set_to_dci(self, irange='AUTO', speed='MED'):
        pass

    @abstractmethod
    def set_to_freq(self):
        pass

    @abstractmethod
    def set_to_thermocouple(self, tctype='J'):
        pass

    @abstractmethod
    def set_to_rtd(self, rtdtype='PT385'):
        pass

    @abstractmethod
    def read(self):
        pass
