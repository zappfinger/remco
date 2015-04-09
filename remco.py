#
#	remco.py	remote commands on a trusted network
#   by zappfinger,
#
#	version:	1.9
#	04AUG2014:	local commands now preceded by '.', e.g.: '.ls'
#	09AUG2014:	using import readline to enable command history, back keys, etc
#	12AUG2014:	.cd was not working, get was not working
#	11SEP2014:	get and put now also work on entire directories, recursive
#	21SEP2014:	better error handling
#	03OCT2014:	show local and remote host names
#	05OCT2014:	added diff function to compare directories
#	13OCT2014:	do not allow diff on local dir<>remote dir
#	06MAR2015:  using Pyro 4.32 now, specify pickle serializer
#	09APR2015:	using subprocess now for most commands, correction for dir/file name same as command
#
#   on the remote server, execute:
#   export PYRO_FLAME_ENABLED=true
#   and
#   python -m Pyro4.utils.flameserver -H x.x.x.x -p 9900
#	where x.x.x.x is IP address of the remote server
#	NOTE: only on Linux/OS X platforms!
#
from __future__ import print_function
import sys, os, datetime
import Pyro4.utils.flame
import readline
import socket

Pyro4.config.SERIALIZER = "pickle"    # flame requires pickle serializer

#	CHANGE THIS TO THE IP ADDRESS OF YOUR REMOTE SYSTEM
#flame = Pyro4.utils.flame.connect("192.168.170.201:9900")
#flame = Pyro4.utils.flame.connect("192.168.170.126:9900")
flame = Pyro4.utils.flame.connect("10.0.1.29:9900")	# my PI

if sys.version_info<(3,0):
    input=raw_input
    
def getstat(fildir):    
    return flame.module("flame.stuff").doCommand('stat ' + fildir)
    
def diff():
	remote = flame.module("flame.stuff").doCommand('ls').split('\n')
	remstat = [[fd, getstat(fd).st_size] for fd in remote if len(fd)>1]
	local = os.popen('ls').read().split('\n')
	locstat = [[fd, os.stat(fd).st_size] for fd in local if len(fd)>1]
	if locstat==remstat:
		return '*** files/dirs appear to be the same ***'
	else:
		return '*** files/dirs appear to be NOT the same ***'
	 
def getFileOrDir(command):
	print(command + '\n')
	fildir = command.replace('get ','')
	try:
		gfile = flame.getfile(fildir)
		newfile = open(fildir,'wb')
		newfile.write(gfile)
		newfile.close()
	except Exception,e:
		lines = "\n".join(Pyro4.util.getPyroTraceback())
		if 'Is a directory' in lines:
			print(os.popen('mkdir ' + fildir).read())	#	create local dir also 
			ret = os.chdir(os.path.abspath(fildir))		#	set as new local dir 
			result = flame.module("flame.stuff").doCommand('cd ' + fildir)	# goto remote dir
			result = flame.module("flame.stuff").doCommand('ls')				# list all files and dirs
			fildirs = result.split('\n')
			for fildir in fildirs:
				if len(fildir)>1:
					getFileOrDir('get ' + fildir)
			#	go one level back (locally and remote) 
			result = flame.module("flame.stuff").doCommand('cd ..')
			ret = os.chdir(os.path.abspath('..'))
		else:
			print(str(e))
			
def putFileOrDir(command):
	print(command + '\n')
	fildir = command.replace('put ','')
	if len(fildir)>1:		# remove targetfile first
		try:
			result = flame.module("flame.stuff").doCommand('rm -rf ' + fildir)
		except:
			pass
		try:	
			flame.sendfile(fildir, open(fildir,'rb').read())
		except Exception,e:
			lines = "\n".join(Pyro4.util.getPyroTraceback())
			#print(lines)
			if 'Is a directory' in lines:
				ret = os.chdir(os.path.abspath(fildir))		#	set as new local dir
				result = flame.module("flame.stuff").doCommand('mkdir ' + fildir)	#	create remote dir also 
				result = flame.module("flame.stuff").doCommand('cd ' + fildir)		#	set as new remote dir
				result = os.popen('ls').read()		# list all files and dirs
				fildirs = result.split('\n')
				for fildir in fildirs:
					if len(fildir)>1:
						putFileOrDir('put ' + fildir)
				#	go one level back (locally and remote) 
				result = flame.module("flame.stuff").doCommand('cd ..')
				ret = os.chdir(os.path.abspath('..'))
			else:
				print(str(e))

Pyro4.config.SERIALIZER = "pickle"  # flame requires pickle serializer

# basic stuff
socketmodule = flame.module("socket")
osmodule = flame.module("os")
print("remote host name=", socketmodule.gethostname())
print()

# upload a module source and call a function, on the server, in this new module
modulesource = open("mystuff.py").read()
flame.sendmodule("flame.stuff", modulesource)

myIP =socket.gethostbyname(socket.gethostname())
myName = socket.gethostname()

while 1:
	localdir = os.popen('pwd').read().strip('\n')
	remotedir = osmodule.getcwd()
	print('local dir (%s): ' % (myName) + localdir);
	print('remote dir (%s): ' % (socketmodule.gethostname())+ remotedir)
	prompt = "Enter command, precede local commands with a dot, e.g.: '.ls' $"
	command = input(prompt)
	if 'get ' in command:
		getFileOrDir(command)
	elif 'put ' in command:
		putFileOrDir(command)
	elif 'diff' in command:	# do diff only if local dir = remote dir
		if localdir == remotedir:
			print(diff())
		else:
			print('*** remote dir and local dir are not the same, cannot do diff! ***')
	elif 'pspy' in command:
		command = 'ps -ef|grep python'
		print(command + '\n')
		result = flame.module("flame.stuff").doCommand(command)
		print(result)
	elif '.cd ' in command:		#  local cd
		dir = command.replace('.cd ','')
		try:
			ret = os.chdir(os.path.abspath(dir))
		except Exception,e:
			print(str(e))			
	elif command.startswith('.'):		# other local commands
		lcomm = command.strip('.')	
		print(os.popen(lcomm).read())
	else:
		print(command + '\n')
		try:
			result = flame.module("flame.stuff").doCommand(command)
		except Exception,e:
			result=str(e)
		#if result <> None or len(result)>1:
		print(result)




