#
#	remco.py	remote commands on a trusted network
#   by zappfinger,
#
#	version:	1.4
#	04AUG2014:	local commands now preceded by '.', e.g.: '.ls'
#	09AUG2014:	using import readline to enable command history, back keys, etc
#	12AUG2014:	.cd was not working, get was not working
#	11SEP2014:	get and put now also work on entire directories, recursive
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

# connect!
#	CHANGE THIS TO THE IP ADDRESS OF YOUR REMOTE SYSTEM
#flame = Pyro4.utils.flame.connect("94.208.133.25:9999")
flame = Pyro4.utils.flame.connect("192.168.56.101:9999")
#flame = Pyro4.utils.flame.connect("10.0.1.3:9999")	# my PI

if sys.version_info<(3,0):
    input=raw_input
    
def getFileOrDir(command):
	print(command + '\n')
	fildir = command.replace('get ','')
	try:
		gfile = flame.getfile(fildir)
		newfile = open(fildir,'wb')
		newfile.write(gfile)
		newfile.close()
	except Exception:
		lines = "\n".join(Pyro4.util.getPyroTraceback())
		if 'Is a directory' in lines:
			print(os.popen('mkdir ' + fildir).read())	#	create local dir also 
			ret = os.chdir(os.path.abspath(fildir))		#	set as new local dir 
			result = flame.module("flameexample.stuff").doCommand('cd ' + fildir)	# goto remote dir
			result = flame.module("flameexample.stuff").doCommand('ls')				# list all files and dirs
			fildirs = result.split('\n')
			for fildir in fildirs:
				if len(fildir)>1:
					getFileOrDir('get ' + fildir)
			#	go one level back (locally and remote) 
			result = flame.module("flameexample.stuff").doCommand('cd ..')
			ret = os.chdir(os.path.abspath('..'))
		else:
			print("%s is not a file or directory..." % fildir)
			
def putFileOrDir(command):
	print(command + '\n')
	fildir = command.replace('put ','')
	if len(fildir)>1:		# remove targetfile first
		#result = flame.module("flameexample.stuff").doCommand('rm ' + file)
		try:	
			flame.sendfile(fildir, open(fildir,'rb').read())
		except Exception:
			lines = "\n".join(Pyro4.util.getPyroTraceback())
			#print(lines)
			if 'Is a directory' in lines:
				ret = os.chdir(os.path.abspath(fildir))		#	set as new local dir
				result = flame.module("flameexample.stuff").doCommand('mkdir ' + fildir)	#	create remote dir also 
				result = flame.module("flameexample.stuff").doCommand('cd ' + fildir)		#	set as new remote dir
				result = os.popen('ls').read()		# list all files and dirs
				fildirs = result.split('\n')
				for fildir in fildirs:
					if len(fildir)>1:
						putFileOrDir('put ' + fildir)
				#	go one level back (locally and remote) 
				result = flame.module("flameexample.stuff").doCommand('cd ..')
				ret = os.chdir(os.path.abspath('..'))
			else:
				print("%s is not a file or directory..." % fildir)


Pyro4.config.SERIALIZER = "pickle"  # flame requires pickle serializer

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
		getFileOrDir(command)
		prevcomm = command
	elif 'put ' in command:
		putFileOrDir(command)
		prevcomm = command
	elif 'pspy' in command:
		command = 'ps -ef|grep python'
		print(command + '\n')
		result = flame.module("flameexample.stuff").doCommand(command)
		prevcomm = command
		print(result)
	elif '.cd ' in command:		#  local cd
		dir = command.replace('.cd ','')
		ret = os.chdir(os.path.abspath(dir))
	elif command.startswith('.'):		# local commands
		lcomm = command.strip('.')	
		print(os.popen(lcomm).read())
	else:
		print(command + '\n')
		result = flame.module("flameexample.stuff").doCommand(command)
		prevcomm = command
		#if result <> None or len(result)>1:
		print(result)




