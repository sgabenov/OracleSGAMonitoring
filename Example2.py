#!/usr/bin/env python
# readSGA.py

from ctypes import *

"""
IPC Resources for ORACLE_SID "test1" :
Shared Memory:
ID		KEY
18481156	0x00000000
18513925	0x00000000
18546694	0xaa5ccb7c

18481156
000000009A034020
"""

shmid     = 458757
sgaBase   = 0x60c00000
ksuseAddr = 0x9A034020
rowCount  = 247
rowSize   = 12512

class SGAException(Exception):
  pass

class ReadSGA:
  libc = cdll.LoadLibrary("/lib64/libc.so.6")
  def __init__(self,shmid,sgaBase):
    self.mem = self.libc.shmat(shmid,sgaBase,010000) # 010000 == SHM_RDONLY
    if self.mem == -1:
      raise SGAException, "can't attach to SGA with id %s" % shmid
  def read1(self,addr):
    val = (c_byte * 1).from_address(addr)
    return val[0]
  def read2(self,addr):
    val = (c_byte * 2).from_address(addr)
    return val[0]+val[1]*256
  def read4(self,addr):
    val = (c_long * 1).from_address(addr)
    return val[0]
  def reads(self,addr,size):
    val = (c_char * size).from_address(addr)
    return val.value
  def __del__(self):
    self.libc.shmdt(self.mem)

def readstatus(statusid,ksuseflg):
  if (statusid & 11 == 1):
    status = 'ACTIVE'
  elif (statusid & 11 == 0):
    if (ksuseflg & 4096 == 0):
      status = 'INACTIVE'
    else:
      status = 'CACHED'
  elif (statusid & 11 == 2):
    status = 'SNIPED'
  elif (statusid & 11 == 3):
    status = 'SNIPED'
  else:
    status = 'KILLED'
  return status

readSGA = ReadSGA(shmid,sgaBase)

# Open a file
fo = open("foo.txt", "wb")
fo.write( "Python is a great language.\nYeah its great!!\n");



print "'select from v$session' made by reading SGA directly:"
print "       SID    SERIAL# USERNAME   MACHINENAME          STATUS                                                             "
print "---------- ---------- ---------- -------------------- --------------------------------------------------------------------"

# MyDefenitions Oracle 11g
memaddr = ksuseAddr
for i in range(1,rowCount):
  ksspaflg = readSGA.read4(memaddr+0)
  ksuseflg = readSGA.read4(memaddr+5936)
  sid      = i
  serial   = readSGA.read2(memaddr+5922)
  username = readSGA.reads(memaddr+6200,30)
  machinename = readSGA.reads(memaddr+6240,64)
  statusid = readSGA.read1(memaddr+5976)
  status   = readstatus(statusid,ksuseflg)
  print "%10d %10d %-10s %-20s %-8s" % (sid, serial, username, machinename, status)
  #if (ksspaflg & 1 != 0) and (ksuseflg & 1 != 0):
    #print "%10d %10d %-10s %-20s %-8s" % (sid,serial,username,machinename,status)
  memaddr += rowSize


# Close opend file
fo.close()

# Backup
"""
memaddr = ksuseAddr
for i in range(1,rowCount):
  ksspaflg = readSGA.read4(memaddr+0)
  ksuseflg = readSGA.read4(memaddr+5936)
  sid      = i
  serial   = readSGA.read2(memaddr+5922)
  username = readSGA.reads(memaddr+6200,30)
  machinename = readSGA.reads(memaddr+6240,64)
  statusid = readSGA.read1(memaddr+5976)
  status   = readstatus(statusid,ksuseflg)
  if (ksspaflg & 1 != 0) and (ksuseflg & 1 != 0):
    print "%10d %10d %-30s %-64s %-8s" % (sid,serial,username,machinename,status)
  memaddr += rowSize
"""


