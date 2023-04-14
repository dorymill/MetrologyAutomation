# MetrologyAutomation

Python OOP Framework containg the core set of SCIPI commands required to develop calibration applications 

--------------------------------------------------------------------------------------------------

Instruments can be initialized in an application as instances of the appropriate instrument class after importing the instrumentation core. Once done, test commands can easily be incorporated in code logic as dictated by procedure.

Addition of instruments is as simple as defining an appropriate class in the core file, inheriting the Init class or related model class--or defining your \_\_init\_\_ constructor as necessary--and defining instrument functions as needed
using 'self.ins' as the name of the general PyVISA resource instance (Ex: self.ins.write('{some command}').

TO-DO: At present the heart of the project resides in the horrific monolith in Core. Abstraction is on the to-do list, but not of immediate concern.
