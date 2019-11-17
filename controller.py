'''
cumulonimbus v0.1 - Copyright 2019 James Slaughter,
This file is part of nimbus v0.1.

nimbus v0.1 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

nimbus v0.1 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with nimbus v0.1.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
controller.py - 
'''

#python imports
import imp
import sys
from array import *

#third-party imports
#No third-party imports

#programmer generated imports
#No programmer generated imports

'''
controller
Class: This class is responsible for maintaining key variable values globally
'''
class controller:
    '''
    Constructor
    '''
    def __init__(self):

        self.debug = False
        self.logfile = ''
        self.FLOG = ''
        self.targetlist = ''
        self.target_list = ''
        self.target = ''
        self.domains = False
        self.files = False
        self.outputdir = ''
        self.output = ''
        self.depth = ''
        self.process = ''
        self.cloud_domains = []
        self.file_types = []
        self.user_agent = ''
