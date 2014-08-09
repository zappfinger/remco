#
#	remco.py	remote commands on a trusted network
#   by zappfinger,
#
#	version:	1.2
#	04AUG2014:	local commands now preceded by '.', e.g.: '.ls'
#	09AUF2014:	using import readline to enable command history, back keys, etc
#
#   on the remote server, execute:
#   export PYRO_FLAME_ENABLED=true
#   and
#   python -m Pyro4.utils.flameserver -H x.x.x.x -p 9999
#	where x.x.x.x is IP address of the remote server
#
from __future__ import print_function
import sys, os
import Pyro4.utils.flame
import readline

if sys.version_info<(3,0):
    input=raw_input

Pyro4.config.SERIALIZER = "pickle"  # flame requires pickle serializer

# connect!
#	CHANGE THIS TO THE IP ADDRESS OF YOUR REMOTE SYSTEM
flame = Pyro4.utils.flame.connect("10.0.1.3:9999")
#flame = Pyro4.utils.flame.connect("192.168.56.101:9999")

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
	print('local dir: ' + os.popen('pwd').read().strip('\n'));
	print('remote dir: ' + osmodule.getcwd())
	prompt = "Enter command, precede local commands with a dot, e.g.: '.ls' $"
	command = input(prompt)
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
	elif '.cd ' in command:		#  local cd
		dir = command.replace('lcd ','')
		ret = os.chdir(os.path.abspath(dir))
	elif command.startswith('.'):		# local commands
		lcomm = command.strip('.')	
		print(os.popen(lcomm).read())
	else:
		print(command + '\n')
		result = flame.module("flameexample.stuff").doCommand(command)
		prevcomm = command
		print(result)




