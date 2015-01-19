#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import math
import pickle
import os
import netsnmp


link_color24 = []
link_color50 = []
dir_trabajo = ''
wire_prop ={'loss':0,'delay':0,'dup':0,'bandwith':0,'speed':0,
				'capacity':0,'damage':0,'channel':'c24GHz'}
password = ''
v_name_base= 'openwrt'

current_wire = []

class NodoList(list):
	def __init__(self):
		self.nl = []
		self.current = None 
		self.run = False
    
	def set_current(self,no):
		self.current = no
    
	def get_current(self):
		return self.current
    
	def set_cur_pos(self,pos):
		for x in self:
			if x.pos==pos:
				self.current = x

nodolist = NodoList()

class interface(object):
    def __init__(self,indice,name,nodonum,oamip):
		self.ind = indice
		self.name = name
		self.oamip = oamip
		self.ifpresent = False
		self.ip ={'tapwrt':'192.168.' + nodonum + '.1','oam':'192.168.100.' + nodonum,
			'lo':None,'eth0':None,'eth1':None,'eth2':None,'bat0':'192.168.7.' + nodonum,}[name]
		self.mac ={'tapwrt':None,'oam':None,'lo':None,'eth0':'8001000007' + nodonum,
			'eth1':'8002000007' +  nodonum,'eth2':'8005000007' + nodonum,
			'bat0':None}[name]
    def rxtx_packets(self):
		if self.ind:
			port = self.ind
			host = self.oamip
			mibr=netsnmp.Varbind('iso.3.6.1.2.1.2.2.1.11.' + str(port))
			rx = netsnmp.snmpget(mibr, Version = 1, DestHost = host,Community='public',
				Timeout=5000,Retries=0)
			mibt=netsnmp.Varbind('iso.3.6.1.2.1.2.2.1.17.' + str(port))
			tx = netsnmp.snmpget(mibt, Version = 1, DestHost = host,Community='public',
				Timeout=5000,Retries=0)
			if rx[0] is None:rx =['0','0']
			if tx[0] is None:tx =['0','0']  
			return(rx[0],tx[0])
	    
    def __str__(self):
	return str(self.name)	
    
    def __del__(self):
	print "Interfase " + self.name + " has been deleted"

class nodoClass(object):
    def __init__(self, p):
		self.pos = p
		self.num = int((p[0] // 100)*10 + p[1]//100)
		self.name = 'wrt' + str(self.num)
		self.octet_str = str(self.num)
		self.smp_ip = '192.168.100.' + str(self)
		self.oam  = interface(None,'oam',str(self),self.smp_ip)
		self.tapwrt =  interface(None,'tapwrt',str(self),self.smp_ip)
		self.lo  =  interface(1,'lo',str(self),self.smp_ip)
		self.eth0 = interface(2,'eth0',str(self),self.smp_ip)
		self.eth1 = interface(3,'eth1',str(self),self.smp_ip)
		self.eth2 = interface(4,'eth2',str(self),self.smp_ip)
		self.bat0=  interface(5,'bat0',str(self),self.smp_ip)		
		self.interfases =[self.tapwrt,self.oam,self.lo,self.eth0,self.eth1,self.eth2,self.bat0]
		self.originator = self.getoriginators()
		self.running = False
		print "Node " + self.name + " has been created"   

    def __str__(self):
		return str(self.num)	

    def __del__(self):
		self.stop()	
		print "Node " + self.name + " has been deleted"

	    
    def stop(self):
		if self.running:
			os.system('echo ' +password+' | sudo -S rm -rf /tmp/c24GHz' + self.octet_str)
			os.system('echo ' +password+' | sudo -S rm -rf /tmp/c50GHz' + self.octet_str)
			os.system('echo ' +password+' | sudo -S ip addr del '+ self.tapwrt.ip +'/24 dev tapwrt' +self.octet_str)
			os.system('echo ' +password+' | sudo -S ip link delete tapwrt' +self.octet_str)
			os.system('VBoxManage controlvm num' + self.octet_str + ' poweroff')
			os.system('VBoxManage unregistervm --delete num' + self.octet_str )
			os.system('killall -q vde_switch') 
			remover_enlaces(None)
			self.running = False


    def get_interfases(self):
		host= self.smp_ip
		infa =['0','0']
		lointerfases =['tapwrt','oam']
		k=1025
		while infa[0] != None:
			var=netsnmp.Varbind('iso.3.6.1.2.1.25.3.2.1.3.'+str(k))
			infa = netsnmp.snmpget(var, Version = 1, DestHost = host,Community='public',Timeout=5000,Retries=0) 
			if infa[0] != None:k=k+1
			if infa[0] != None:lointerfases.append(infa[0].split()[2])
		for i in  interfases:
			if i in lointerfases:i.ifpresent=True
    
    def getoriginators(self):
		host= self.smp_ip
		mibr=netsnmp.Varbind('iso.3.6.1.4.1.32.1.1.101.1')
		orig = netsnmp.snmpget(mibr, Version = 1, DestHost = host,Community='public',Timeout=5000,Retries=0)
		return str(orig[0]).split()	    
	
    def start(self):
		if not self.running:
			os.system('echo ' +password+' | sudo -S ip tuntap add tapwrt'+self.octet_str+' mode tap')
			os.system('echo ' +password+' | sudo -S ifconfig tapwrt'+self.octet_str+' ' +self.tapwrt.ip + ' up')
			os.system('vde_switch -d --hub -s /tmp/c24GHz'+self.octet_str+' -tap tapwrt'+self.octet_str+' -m 666 -f '+ dir_trabajo + '/colourful.rc')
			os.system('vde_switch -d --hub -s /tmp/c50GHz'+self.octet_str+' -tap tapwrt'+self.octet_str+' -m 666 -f '+ dir_trabajo + '/colourful.rc')        
			os.system('VBoxManage clonevm ' + v_name_base + ' --name num'+self.octet_str+' --register')
			os.system('VBoxManage modifyvm num'+self.octet_str+' --nic1 hostonly --hostonlyadapter1 vboxnet0 --macaddress1 ' + self.eth0.mac)
			os.system('VBoxManage modifyvm num'+self.octet_str+' --nic2 generic --nicgenericdrv2 VDE --nicproperty2 network=/tmp/c24GHz'+self.octet_str+'[2] --macaddress2 ' + self.eth1.mac)       
			os.system('VBoxManage modifyvm num'+self.octet_str+' --nic3 generic --nicgenericdrv3 VDE --nicproperty3 network=/tmp/c50GHz'+self.octet_str+'[3] --macaddress3 ' + self.eth2.mac)
			os.system('VBoxManage startvm num'+self.octet_str ) # + '--type headless'
			self.running = True
			print self.eth0.mac
		
class wireClass(object):
	def __init__(self,src,dst,quality):
		self.s = src
		self.d = dst
		self.sd = src,dst
		self.ds = dst,src
		self.quality = quality
		self.s_str = str(int(self.s[0]//100)) + str(int(self.s[1]//100))
		self.d_str = str(int(self.d[0]//100)) + str(int(self.d[1]//100)) 
		self.name = "wire" +self.s_str+'-' + self.d_str
		self.canal =self.quality['channel']
		self.prop ={'loss':self.quality['loss'],'delay':self.quality['delay'],'dup':self.quality['dup'],
				'bandwith':self.quality['bandwith'],'speed':self.quality['speed'],'capacity':self.quality['capacity'],
				'damage':self.quality['damage'],'channel':self.quality['channel']}

	def __del__(self):
		os.system('killall -q wirefilter') 

	def  start(self):
		os.system('wirefilter'+' --daemon -v /tmp/' + self.canal + self.s_str +':/tmp/'+ self.canal  + self.d_str)	
   
	def stop(self):
		os.system('killall -q wirefilter') 


def get_packets(signal):
    for n in nodolist:
	for i in n.interfases:
		print i.rxtx_packets()	
	    
def point2num(point):
    return int((point[0] // 100)*10 + point[1]//100)

#set point close to cuadricul intersection
def near(punto):
	x,y = punto
	xi,xd = divmod(x, 100)
	yi,yd = divmod(y, 100)
	if xd > 50:
		if xi < 10: xi =xi+1
	if yd > 50:
		yi =yi+1
	return xi*100,yi*100

def open_mesh(widget):
	global nodo,link_color24,link_color50,nodolist
	dialog = gtk.FileChooserDialog("Select work directory",
		None,
		gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	response = dialog.run()
	if response == gtk.RESPONSE_OK:
		file_path = dialog.get_filename()    
		with open(file_path, 'rb') as f:
			nodolist,link_color24,link_color50 = pickle.load(f)
		archivo_corriente = file_path
		dialog.destroy()
    
def responseToDialog(entry, dialog, response):
    dialog.response(response) 

def getPassword():

    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
    dialog.set_markup('Please enter your <b>password</b>:')
    #create the text input field
    entry = gtk.Entry()
    #allow the user to press enter to do ok
    entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
    entry.set_visibility(False)
    #create a horizontal box to pack the entry and a label
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label("Password:"), False, 5, 5)
    hbox.pack_end(entry)
    #some secondary text
    dialog.format_secondary_markup("This will be used for create interfaces in your local machine")
    #add it and show it
    dialog.vbox.pack_end(hbox, True, True, 0)
    dialog.show_all()
    #go
    dialog.run()
    text = entry.get_text()
    dialog.destroy()
    return text    

def run_mesh(signal):
	global nodolist
	for n in nodolist:
		n.start()
	start_wirefilter()
	os.system('echo ' +password+' | sudo -S ifconfig vboxnet0 inet 192.168.100.1 up')
	nodolist.run = True

def start_wirefilter():  
	for n in link_color24:
		n.start()
	for n in link_color50:
		n.start()
	  
def stop_mesh(signal):
	global nodolist
	os.system('killall -q wirefilter') 
	os.system('killall -q vde_switch') 
	for n in nodolist:
		n.stop()
		os.system('echo ' +password+' | sudo -S ip addr del 192.168.100.1/24 dev vboxnet0')
		os.system('echo ' +password+' | sudo -S ip link set vboxnet0 down')
		nodolist.run = False
     

def save_mesh(signal):
	dialog = gtk.FileChooserDialog("Select work directory",
		None,
		gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	response = dialog.run()
	if response == gtk.RESPONSE_OK:
		file_path = dialog.get_filename()    
		datos =nodolist,link_color24,link_color50
		with open(file_path, 'wb') as f:
			pickle.dump(datos, f)
		archivo_corriente = file_path
		dialog.destroy()

def remover_nodos(signal):
    global nodolist,link_color24,link_color50
    link = [(j.sd) for j in link_color24]
    print link	
    o = [(j[0]) for j in link]	
    d = [(j[1]) for j in link]
    link = [(j.sd) for j in link_color50]
    print link	
    o5 = [(j[0]) for j in link]	
    d5 = [(j[1]) for j in link]
    for i in nodolist[:]:
		if (i.pos not in o and i.pos not in d) and (i.pos not in o5 and i.pos not in d5) : nodolist.remove(i)

def remover_enlaces(signal):    
	global nodolist,link_color24,link_color50
	n = [(j.pos) for j in nodolist]
	for i in link_color24[:]:	
		linea= i.sd
		((x1,y1),(x2,y2))=linea
		if (x1,y1) not  in n or (x2,y2) not in n: link_color24.remove(i)
	for i in link_color50[:]:	
		linea= i.sd
		((x1,y1),(x2,y2))=linea
		if (x1,y1) not  in n or (x2,y2) not in n: link_color50.remove(i)
	if nodolist.run:
		start_wirefilter()

def select_folder(signal):
	global dir_trabajo
	dialog = gtk.FileChooserDialog("Select work directory",
		None,
		gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
		gtk.STOCK_OPEN, gtk.RESPONSE_OK))

	response = dialog.run()
	if response == gtk.RESPONSE_OK:
		dir_trabajo = dialog.get_filename()
	dialog.destroy()



# Create a new backing pixmap of the appropriate size
def configure_event(widget, event):

    return True	
    
def dibujar(widget):
	global cr
	cr = widget.window.cairo_create()
	w = widget.allocation.width
	h = widget.allocation.height
	cr.set_source_rgb(0.0, 0.0, 0.0)
	cr.rectangle(0, 0, w, h)
	cr.fill()
	#Draw bacground grid
	cr.set_line_width(1)
	cr.set_source_rgba(0.1, 0.1, 0.1,1.0)
	for i in range(11):
		cr.move_to(i*100, 0)
		cr.line_to(i*100, 1000)
	for i in range(11):
		cr.move_to(0,i*100)
		cr.line_to(1000,i*100)
	cr.stroke()
	#Draw wire
	cr.select_font_face('Sans')
	cr.set_font_size(12)
	for l in link_color24:
		if l.sd in current_wire:
			cr.set_source_rgba(1.0, 1.0, 1.0,1.0) 
			cr.set_line_width (2.0)
			#Draw wire property for current nodo
			i=0
			for p in l.prop:
				cr.move_to(i*100,30)
				cr.show_text(p +': ' + str(l.prop[p]))
				i+=1
		
		else: 
			cr.set_source_rgba(1.0, 1.0, 0.1,1.0) 
			cr.set_line_width (1.0)
		(xi,yi),(xf,yf) = l.sd
		cr.move_to(xi,yi)
		cr.line_to(xf,yf)
		cr.stroke() 
	for l in link_color50:
		if l.sd in current_wire:
			cr.set_source_rgba(1.0, 1.0, 1.0,1.0) 
			cr.set_line_width (2.0)
			#Draw wire property for current nodo
			i=0
			for p in l.prop:
				cr.move_to(i*100,45)
				cr.show_text(p +': ' + str(l.prop[p]))
				i+=1
		
		else: 
			cr.set_source_rgba(1.0, 1.0, 0.1,1.0) 
			cr.set_line_width (1.0)
		(xi,yi),(xf,yf) = l.sd
		cr.move_to(xi,yi)
		cr.line_to(xf,yf)
		cr.stroke() 
	#Draw nodo	
	for po in nodolist:
		p =po.pos
		cr.arc(p[0],p[1], 12, 0, 2*math.pi)
		if po.pos == nodolist.current.pos:
			#Draw originators for curren nodo
		    o = po.getoriginators()
		    if o != ['None']:po.originator = o
		    for i in range(len(po.originator)):
			cr.move_to(125*(i%8),920+(i//8)*15)
			cr.show_text(str(po.originator[i]))
			#Drow Interface packets for curren nodo
		    for i in po.interfases:
			if i.ind:
			    r,t = i.rxtx_packets()
			    cr.move_to(200*(i.ind-1),15)
			    cr.show_text(i.name+' rx: '+r+' tx: '+t)
			
		    cr.set_source_rgba(0.3, 1.0, 0.3,1.0) 
		else:
		    cr.set_source_rgba(0.1,0.6, 0.1,1.0) 
		cr.fill()
		cr.stroke()
		#Draw bat0 packets for each nodo
		cr.set_source_rgb(1.0, 0.1, 0.1)
		cr.move_to(p[0]-7,p[1]+5)
		cr.show_text(str(po))
		cr.move_to(p[0]-30,p[1]-30)
		cr.show_text('Rx:'+str(po.bat0.rxtx_packets()[0]))
		cr.move_to(p[0]-30,p[1]-15)
		cr.show_text('Tx:'+str(po.bat0.rxtx_packets()[0]))
	cr.stroke()
# Redraw the screen from the backing pixmap
def expose_event(widget, event):
    dibujar(widget)  
    return False


def button_press_event(widget, event):
	global inicio
	if cr != None:
		inicio = near((event.x, event.y))
	return True

def button_release_event(widget, event):
	global link_color24,link_color50,wire_prop,current_wire,nodolist
	fin = near((event.x, event.y))
	if event.button == 1 and cr != None:
		if inicio==fin:
			if not any(x.pos==inicio for x in nodolist):
				nodolist.append(nodoClass(inicio))
		    	nodolist.set_cur_pos(inicio)
		elif wire_prop['channel'] == 'c24GHz':
			current_wire = [(inicio,fin),(fin,inicio)]
			if any(x.pos in [inicio,fin] for x in nodolist):
				if (not any(x.sd in current_wire  for x in link_color24)):
					link_color24.append(wireClass(inicio,fin, wire_prop))
					if nodolist.run: start_wirefilter()
				else:
					for x in link_color24: 
						if x.ds in current_wire:
							wire_prop = x.prop
							print current_wire
							print x.prop
		elif wire_prop['channel'] == 'c50GHz':
			current_wire = [(inicio,fin),(fin,inicio)]
			if any(x.pos in [inicio,fin] for x in nodolist):
				if (not any(x.sd in current_wire  for x in link_color50)):
					link_color50.append(wireClass(inicio,fin, wire_prop))
					if nodolist.run: start_wirefilter()
				else:
					for x in link_color50: 
						if x.ds in current_wire:
							wire_prop = x.prop
							print current_wire
							print x.prop
	if event.button == 2 and cr != None:
		if inicio==fin:
			if any(x.pos==inicio for x in nodolist):
				nodolist.set_cur_pos(inicio)
		elif wire_prop['channel'] == 'c24GHz':
			current_wire = [(inicio,fin),(fin,inicio)]
			if any(x.pos in [inicio,fin] for x in nodolist):
				if any(x.sd in current_wire  for x in link_color24):
					if nodolist.run: start_wirefilter()
					for x in link_color24: 
						if x.ds in current_wire:
							wire_prop = x.prop
		elif wire_prop['channel'] == 'c50GHz':
			current_wire = [(inicio,fin),(fin,inicio)]
			if any(x.pos in [inicio,fin] for x in nodolist):
				if any(x.sd in current_wire  for x in link_color50):
					if nodolist.run: start_wirefilter()
					for x in link_color50: 
						if x.ds in current_wire:
							wire_prop = x.prop

	elif event.button == 3 and cr != None:
		if inicio==fin:
			if any(x.pos==inicio for x in nodolist):
				for x in nodolist:
					if x.pos==inicio:
						nid=nodolist.index(x)
						i = nodolist.pop(nid)
						del(i)
		elif wire_prop['channel'] == 'c24GHz':
			if any(x.sd==(inicio,fin) for x in link_color24):
				for x in link_color24:
					if x.sd==(inicio,fin):
						lid=link_color24.index(x)
						i = link_color24.pop(lid)
						del i
				if nodolist.run: start_wirefilter()
			elif any(x.sd==(fin,inicio) for x in link_color24):
				for x in link_color24:
					if x.sd==(fin,inicio):
						lid=link_color24.index(x)
						i = link_color24.pop(lid)
						del i
				if nodolist.run: start_wirefilter()
 		elif wire_prop['channel'] == 'c50GHz':
			if any(x.sd==(inicio,fin) for x in link_color50):
				for x in link_color50:
					if x.sd==(inicio,fin):
						lid=link_color50.index(x)
						i = link_color50.pop(lid)
						del i
				if nodolist.run: start_wirefilter()
			elif any(x.sd==(fin,inicio) for x in link_color50):
				for x in link_color50:
					if x.sd==(fin,inicio):
						lid=link_color50.index(x)
						i = link_color50.pop(lid)
						del i
				if nodolist.run: start_wirefilter()   
	dibujar(widget)
	return True

def wire_show(signal):
	wire()
	
def menuitem_response():
    return
def scale_set_default_values(scale):
    scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
    scale.set_digits(1)
    scale.set_value_pos(gtk.POS_TOP)
    scale.set_draw_value(True)

def on_changed(widget):
	global wire_prop
	val = widget.get_value()
	name = widget.get_name()
	wire_prop[name] = val


def callback(self, button):
	global wire_prop
	wire_prop['channel']= button



class wire(gtk.Window):
	def __init__(self): 
		super(wire, self).__init__()
		self.set_size_request(400, 700)
		self.set_border_width(10)
		self.set_title("WIREFILTER SETUP")
		self.connect("delete_event", lambda w,e: self.destroy())

		vbox_app = gtk.VBox(False, 0)
		self.add(vbox_app)
		vbox_app.show()
		vbox1 = gtk.VBox(False, 0)
	
		label1 = gtk.Label("Percentage of loss: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()
	
		adj1 = gtk.Adjustment(wire_prop['loss'], 0.0, 101.0, 1.0, 1.0, 1.0)
		vscale1 = gtk.HScale(adj1)
		scale_set_default_values(vscale1)
		vscale1.set_name('loss')
		vbox1.pack_start(vscale1, True, True, 0)
		vscale1.connect("value-changed",on_changed)
		vscale1.show()
	
		label1 = gtk.Label("Extra  delay in milliseconds: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()
		
		adj2= gtk.Adjustment(wire_prop['delay'], 0.0, 1001.0, 1.0, 1.0, 1.0)
		vscale2 = gtk.HScale(adj2)
		scale_set_default_values(vscale2)
		vscale2.set_name('delay')
		vbox1.pack_start(vscale2, True, True, 0)
		vscale2.connect("value-changed",on_changed)
		vscale2.show()

		label1 = gtk.Label("dup percentage of dup packet: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()	

		adj3= gtk.Adjustment(wire_prop['dup'], 0.0, 101.0, 1.0, 1.0, 1.0)
		vscale3 = gtk.HScale(adj3)
		scale_set_default_values(vscale3)
		vscale3.set_name('dup')
		vbox1.pack_start(vscale3, True, True, 0)
		vscale3.connect("value-changed",on_changed)
		vscale3.show()	

		label1 = gtk.Label("Channel bandwidth in Bytes/sec: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()	

		adj4= gtk.Adjustment(wire_prop['bandwith'], 0.0, 1001.0, 1.0, 1.0, 1.0)
		vscale4 = gtk.HScale(adj4)
		scale_set_default_values(vscale4)
		vscale4.set_name('bandwith')
		vbox1.pack_start(vscale4, True, True, 0)
		vscale4.connect("value-changed",on_changed)
		vscale4.show()

		label1 = gtk.Label("Interface  speed  in  Bytes/sec: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()	

		adj5= gtk.Adjustment(wire_prop['speed'], 0.0, 1001.0, 1.0, 1.0, 1.0)
		vscale5 = gtk.HScale(adj5)
		scale_set_default_values(vscale5)
		vscale5.set_name('speed')
		vbox1.pack_start(vscale5, True, True, 0)
		vscale5.connect("value-changed",on_changed)
		vscale5.show()

		label1 = gtk.Label("Channel  capacity  in Bytes: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()
	
		adj6= gtk.Adjustment(wire_prop['capacity'], 0.0, 1001.0, 1.0, 1.0, 1.0)
		vscale6 = gtk.HScale(adj6)
		scale_set_default_values(vscale6)
		vscale6.set_name('capacity')
		vbox1.pack_start(vscale6, True, True, 0)
		vscale6.connect("value-changed",on_changed)
		vscale6.show()

		label1 = gtk.Label("Number of bits damaged/one megabyt: ")
		vbox1.pack_start(label1, True, True, 0)
		label1.show()
	
		adj7= gtk.Adjustment(wire_prop['damage'], 0.0, 101.0, 1.0, 1.0, 1.0)
		vscale7 = gtk.HScale(adj7)
		scale_set_default_values(vscale7)
		vscale7.set_name('damage')
		vbox1.pack_start(vscale7, True, True, 0)
		vscale7.connect("value-changed",on_changed)
		vscale7.show()
		
		hbox1 = gtk.HBox(gtk.FALSE, 0)
		hbox1.set_border_width(10)
		vbox1.pack_start(hbox1, gtk.TRUE, gtk.TRUE, 0)
		hbox1.show()
		
		button = gtk.RadioButton(None, "2.4 GHz")
		button.connect("toggled", callback, "c24GHz")
		if wire_prop['channel'] =="2.4 GHz": button.set_active(gtk.TRUE)
		hbox1.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
		button.show()
		button = gtk.RadioButton(button, "5.0 GHz")
		button.connect("toggled", callback, "c50GHz")
		if wire_prop['channel'] =="5.0 GHz": button.set_active(gtk.TRUE)
		hbox1.pack_start(button, gtk.TRUE, gtk.TRUE, 0)
		button.show()
	
		button_set = gtk.Button(stock=gtk.STOCK_OK)
		button_set.connect("clicked", lambda w: self.destroy())
		button_set.set_flags(gtk.CAN_DEFAULT)
		hbox1.pack_start(button_set, True, True, 0)
		button_set.show()	
	
		button_close = gtk.Button(stock=gtk.STOCK_CLOSE)
		button_close.connect("clicked", lambda w: self.destroy())
		button_close.set_flags(gtk.CAN_DEFAULT)
		hbox1.pack_start(button_close, True, True, 0)
		button_close.show()

		vbox1.show()
		vbox_app.add(vbox1)

		button_close.grab_default() 

		self.show()
		


class MenuApp(gtk.Window):
	def __init__(self):
		super(MenuApp, self).__init__()
		self.set_title("Mesh network emulator")
		self.set_size_request(1001, 1100)
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))
		self.set_position(gtk.WIN_POS_CENTER)
        # top level menu bar
		menubar = gtk.MenuBar()
 
        # top items on the menu bar
		filem = gtk.MenuItem("File")
		editm = gtk.MenuItem("Edit")
		runm = gtk.MenuItem("Run/Stop")
		toolsm = gtk.MenuItem("Tools")
		aboutm = gtk.MenuItem("About")
 
        # now, create for FILE item the menu
		filemenu = gtk.Menu()
		filem.set_submenu(filemenu)        
 
        # create the items for File menu
		new = gtk.MenuItem("New")
		filemenu.append(new)
		new.connect("activate", select_folder)

		open = gtk.MenuItem("Open")
		filemenu.append(open)
		open.connect("activate", open_mesh)
 
		save = gtk.MenuItem("Save")
		filemenu.append(save)
 
		saveas = gtk.MenuItem("Save as")
		filemenu.append(saveas)
		saveas.connect("activate", save_mesh)
	# separator
		separat = gtk.SeparatorMenuItem()
		filemenu.append(separat)
 
        # now, Quit item with accelerator and image
        # generic accelerator
		agr = gtk.AccelGroup()
		self.add_accel_group(agr)
 
		quitImg = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
		key, mod = gtk.accelerator_parse("Q")
		quitImg.add_accelerator("activate", agr, key, mod, gtk.ACCEL_VISIBLE)
		filemenu.append(quitImg)
 
        # connect to Quit the activate event
		quitImg.connect("activate", gtk.main_quit)

	# create the edit menu and attach it to the top item
		editmenu = gtk.Menu()
		editm.set_submenu(editmenu)
	  
	# create the items for Edit menu
		delmesh = gtk.MenuItem("Delete Mesh")
		editmenu.append(delmesh)
	
		delnodo = gtk.MenuItem("Delete Nodo")
		editmenu.append(delnodo)
		delnodo.connect("activate",remover_nodos)
		
		dellink = gtk.MenuItem("Delete Link")
		editmenu.append(dellink)	
		dellink.connect("activate", remover_enlaces)
		
		editwire = gtk.MenuItem("Edit Wire")
		editmenu.append(editwire)	
		editwire.connect("activate", wire_show)
		
	# create the run menu and attach it to the top item
		runmenu = gtk.Menu()
		runm.set_submenu(runmenu)
	
        # create the items for Run menu
		run = gtk.MenuItem("Run")
		runmenu.append(run)
		run.connect("activate", run_mesh)
		
		stop = gtk.MenuItem("Stop")
		runmenu.append(stop)
		stop.connect("activate", stop_mesh)
		
	# create the tools menu and attach it to the top item
		toolsmenu = gtk.Menu()
		toolsm.set_submenu(toolsmenu)
	
        # create the items for Run menu
		snmp = gtk.MenuItem("SNMP")
		toolsmenu.append(snmp) 
		snmp.connect("activate",get_packets)
		
        # append the top items
		menubar.append(filem)
		menubar.append(editm)
		menubar.append(runm)
		menubar.append(toolsm)
		menubar.append(aboutm)
 
        # pack in a vbox
		vbox = gtk.VBox(False, 2)
		vbox.pack_start(menubar, False, False, 0)

	# Create the drawing area
		drawing_area = gtk.DrawingArea()
		drawing_area.set_size_request(1000, 1000)
		drawing_area.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
		vbox.pack_start(drawing_area, True, True, 0)
		drawing_area.show() 

	# Signals used to handle backing pixmap
		drawing_area.connect("expose_event", expose_event)
		drawing_area.connect("configure_event", configure_event)

	# Event signals

		drawing_area.connect("button_press_event", button_press_event)
		drawing_area.connect("button_release_event", button_release_event)
	
		drawing_area.set_events(gtk.gdk.EXPOSURE_MASK
						| gtk.gdk.LEAVE_NOTIFY_MASK
						| gtk.gdk.BUTTON_PRESS_MASK
						| gtk.gdk.BUTTON_RELEASE_MASK
						| gtk.gdk.BUTTON3_MOTION_MASK    
						| gtk.gdk.POINTER_MOTION_MASK
						| gtk.gdk.POINTER_MOTION_HINT_MASK)	
        

	# add the vbox to the window
		self.add(vbox)
		self.connect("destroy", gtk.main_quit)

		self.show_all()
		gobject.timeout_add( 1000, self.tick )
		global password
		password = getPassword()
		dir_trabajo = os.getcwd()
		print password,dir_trabajo

	def tick (self):
	    self.queue_draw()
	    return True


 

MenuApp()

gtk.main()