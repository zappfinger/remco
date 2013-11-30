#
#	remco.py	remote commands on a trusted network 
#
from __future__ import print_function
import sys, os
import Pyro4.utils.flame

if sys.version_info<(3,0):
    input=raw_input

Pyro4.config.SERIALIZER = "pickle"  # flame requires pickle serializer

# connect!
#	CHANGE THIS TO THE IP ADDRESS OF YOUR REMOTE SYSTEM
flame = Pyro4.utils.flame.connect("192.168.2.2:9999")

# basic stuff
socketmodule = flame.module("socket")
osmodule = flame.module("os")
print("remote host name=", socketmodule.gethostname())
print()
#print("remote server current directory=", osmodule.getcwd())

# upload a module source and call a function, on the server, in this new module
modulesource = open("mystuff.py").read()
flame.sendmodule("flameexample.stuff", modulesource)
prevcomm = 'pwd'

while 1:
	prompt = osmodule.getcwd() + '$ '
	command = input(prompt)
	if len(command) == 3:	# if UP arrow, then previous command!
		if (ord(command[0])) == 27 and (ord(command[2])) == 65:
			command = prevcomm
	if 'get ' in command:
		print(command + '\n')
		file = command.replace('get ','')
		flame.getfile(file)
		prevcomm = command
	elif 'put ' in command:
		print(command + '\n')
		file = command.replace('put ','')
		if len(file)>1:		# remove targetfile first
			result = flame.module("flameexample.stuff").doCommand('rm ' + file)	
			flame.sendfile(file, open(file).read())
		prevcomm = command
	elif 'pspy' in command:
		command = 'ps -ef|grep python'
		print(command + '\n')
		result = flame.module("flameexample.stuff").doCommand(command)
		prevcomm = command
		print(result)
	elif 'lls' in command:		# local ls
		print('local ls \n')	
		print(os.popen('ls').read())
	elif 'lcd ' in command:		#  local cd
		dir = command.replace('lcd ','')
		ret = os.chdir(os.path.abspath(dir))
	else:
		print(command + '\n')
		result = flame.module("flameexample.stuff").doCommand(command)
		prevcomm = command
		print(result)




