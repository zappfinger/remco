# 	this module will be sent to the server as 'flame.stuff'
# 	used by remco.py
#	by: zappfinger
#	update: 02AUG2014, added SQLite class
#	update: 01OCT2014, added insert and delete command
#	update: 05OCT2014, added stat command
#	update: 28MAR2015, name is 'flame.stuff' 
#	update: 09APR2015, use subprocess, correct for dir name equals command (like 'static')
#
from __future__ import print_function
import os, subprocess, random, sqlite3, sys, time
from functools import partial

#
class db(object):
	def __init__( self ):
		#self.DBFILE = "/home/breplu/Desktop/MyPython/gateway/gateway.db"
		self.DBFILE = "/data/rtng/software/gateway.db"

		self.conn = sqlite3.connect( self.DBFILE )
		self.cur = self.conn.cursor()

	def insert(self, insq):
		self.cur.execute(insq)
		self.conn.commit()
		
	def delete(self, delq):
		self.cur.execute(delq)
		self.conn.commit()

	def select(self, selq):
		self.cur.execute('select ' + selq)
		rows = self.cur.fetchall()
		return rows

def doCommand(command):
	if 'cd ' in command:
		dir = command.replace('cd ','')
		#print(dir)
		ret = os.chdir(os.path.abspath(dir))
	elif 'stat ' in command:
		ret = os.stat(command.replace('stat ',''))
	elif 'con' in command:
		db1=db()
		ret = db1.conn
	elif 'select ' in command:
		sel = command.replace('select ','')
		db1 = db()
		ret = db1.select(sel)
	elif 'insert ' in command:
		db1 = db()
		ret = db1.insert(command)
	elif 'delete ' in command:
		db1 = db()
		ret = db1.delete(command)
	else:
		print ('command: ' + command)
		ret = subprocess.call(command, shell=True)
	return ret
    


  