# 	this module will be sent to the server as 'flameexample.stuff'
# 	used by remco.py
#	by: zappfinger
#	update: 02AUG2014, added SQLite class
#
from __future__ import print_function
import os, random, sqlite3, sys, time
from functools import partial

#
class db(object):
	def __init__( self ):
		self.DBFILE = "/home/breplu/Desktop/Newdb.rdb"

		self.conn = sqlite3.connect( self.DBFILE )
		self.cur = self.conn.cursor()

	def insert(self, insq, tup):
		self.cur.execute(insq, tup)
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
	elif 'con' in command:
		db1=db()
		ret = db1.conn
	elif 'sel' in command:
		db1 = db()
		ret = db1.select('name,tempo from patterns')
	else:
		ret = os.popen(command).read()
	return ret
    


  