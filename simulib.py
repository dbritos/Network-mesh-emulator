#!/usr/bin/env python
import netsnmp
from time import sleep
import Tkinter, tkFileDialog

def ing_pas():
    password = tkSimpleDialog.askstring('Ingrese password', 'password')
  

def point2num(point):
    return (point[0] // 100)*10 + point[1]//100

def near(punto):
	x,y = punto
	xi,xd = divmod(x, 100)
	yi,yd = divmod(y, 100)
	if xd > 50:
		if xi < 10: xi =xi+1
	if yd > 50:
		yi =yi+1
	return xi*100,yi*100
	
def nodoup(nodo):
    var=netsnmp.Varbind('iso.3.6.1.2.1.25.3.2.1.3.1025')
    for n in nodo: 
        x,y =n
        nn = (x // 100)*10 + y//100
        hostip = '192.168.100.'+ str(nn)
        infa =[None,None]
        while infa[0] == None:
            sleep(2)
            infa = netsnmp.snmpget(var, Version = 1, DestHost = hostip,Community='public',Timeout=5000,Retries=0)    
	    
def get_interfases(host):
    infa =['0','0']
    interfases =[]
    k=1025
    while infa[0] != None:
        var=netsnmp.Varbind('iso.3.6.1.2.1.25.3.2.1.3.'+str(k))
        infa = netsnmp.snmpget(var, Version = 1, DestHost = host,Community='public',Timeout=5000,Retries=0) 
        if infa[0]!=None:k=k+1
        if infa[0] != None:interfases.append(infa[0].split()[2])
    return interfases 
    
def getpackets(host,port):
    mibr=netsnmp.Varbind('iso.3.6.1.2.1.2.2.1.11.' + str(port))
    rx = netsnmp.snmpget(mibr, Version = 1, DestHost = host,Community='public',Timeout=5000,Retries=0)
    mibt=netsnmp.Varbind('iso.3.6.1.2.1.2.2.1.17.' + str(port))
    tx = netsnmp.snmpget(mibt, Version = 1, DestHost = host,Community='public',Timeout=5000,Retries=0)
    if rx[0] is None:rx =['0','0']
    if tx[0] is None:tx =['0','0']  
    return(rx[0],tx[0])
    
def getoriginators(host):
    mibr=netsnmp.Varbind('iso.3.6.1.4.1.32.1.1.101.1')
    return netsnmp.snmpget(mibr, Version = 1, DestHost = host,Community='public',Timeout=5000,Retries=0)

