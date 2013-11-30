# this module will be sent to the server as 'flameexample.stuff'

from __future__ import print_function
import os

def doCommand(command):
	if 'cd ' in command:
		dir = command.replace('cd ','')
		#print(dir)
		ret = os.chdir(os.path.abspath(dir))
	else:
		ret = os.popen(command).read()
	return ret
    


  