#v1.0
from Tkinter import *
import Tkinter, tkFileDialog
import tkSimpleDialog
import os
import pickle
import shlex,subprocess
import paramiko
import netsnmp
import ttk
from time import sleep

def nodoup():
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
    else:status[host]=1
    if tx[0] is None:tx =['0','0']  
    else:status[host]=1
    return(rx[0],tx[0])
    


def ing_pas():
    password = tkSimpleDialog.askstring('Ingrese password', 'password')
   
def dibujar():
    global link_color,nodo,run,vms,interfase
    w.delete(ALL)
    for i in range(11):
        w.create_line(i*100, 0, i*100, 1000,fill=colorhex(20,20,20))
    for i in range(10):
        w.create_line(0,i*100, 1050,i*100,fill=colorhex(20,20,20))
    for l in link_color:
        linea,col,pid = l
        r,g,b =col
        (lix,liy),(lfx,lfy) = linea
        if (g,b)==(255,255):
            w.create_line(lix,liy,lfx,lfy,fill=colorhex(r,g,b),width=r*5//255)
        else:
            w.create_line(lix,liy,lfx,lfy,fill=colorhex(r,g,b),dash=(1,1),width=r*5//255)
    for n in nodo: 
        x,y =n
        r = 12
        nn = (x // 100)*10 + y//100
        if n == current_nodo:
            w.create_oval(x-r, y-r, x+r, y+r,fill=colorhex(100,255,0))
        else:
            w.create_oval(x-r, y-r, x+r, y+r,fill=colorhex(0,180,0))
        w.create_text(x,y ,text=str(nn))
        hostip = '192.168.100.'+ str(nn)
        if run == 1:
            txp=getpackets(hostip,interfase)
            w.create_text(x,y-40 ,text='Rx '+txp[0],fill=colorhex(0,255,0))
            w.create_text(x,y-20 ,text='Tx '+txp[1],fill=colorhex(0,255,0))
        else:status[hostip]=0
    if curren_nodo_int != [] and run==1:
        for i in range(len(curren_nodo_int)):
            w.create_text(100+200*i,20 ,text=curren_nodo_int_name[i]+' Rx '+curren_nodo_int[i][0]+ ' Tx '+curren_nodo_int[i][1],fill=colorhex(0,255,0))
        w.create_text(100,30 ,text='Interfase seleccionada: '+curren_nodo_int_name[interfase-1],fill=colorhex(100,255,0))

    w.after(4000,dibujar)        


def showint(inicio):
    global curren_nodo_int,curren_nodo_int_name
    x,y =inicio
    curren_nodo_int=[]
    curren_nodo_int_name=[]
    nn = (x // 100)*10 + y//100
    hostip = '192.168.100.'+ str(nn)
    if status[hostip]==1:
        for i in range(len(intface[hostip])):
            curren_nodo_int_name.append(intface[hostip][i])
            curren_nodo_int.append(getpackets(hostip,i+1))
 

    
def on_button_press(event):
    global inicio,nodo,current_nodo
    inicio = near((event.x,event.y))
    if inicio in nodo and run ==1:
        showint(inicio)
        current_nodo = inicio
    
def select_dir():  
    global dir_trabajo
    dir_trabajo = tkFileDialog.askdirectory()
    borra_topo() 

def save_list():
    global link_color,nodo ,archivo_corriente
    file_path = tkFileDialog.asksaveasfilename()
    datos =nodo,link_color
    with open(file_path, 'wb') as f:
		pickle.dump(datos, f)
    archivo_corriente = file_path

def save_corriente():
    global link_color,nodo ,archivo_corriente
    file_path = archivo_corriente
    datos =nodo,link_color
    with open(file_path, 'wb') as f:
		pickle.dump(datos, f)

def open_list():
    global link_color,nodo,archivo_corriente
    file_path = tkFileDialog.askopenfilename()
    with open(file_path, 'rb') as f:
		nodo,link_color = pickle.load(f)
    archivo_corriente = file_path
    dibujar()

def progresbar(): 
    global intface 
    pb = Tk()
    pb.title('Iniciando maquinas  virtuales')
    progressbar = ttk.Progressbar(pb, orient = HORIZONTAL, mode = 'indeterminate',length=500)
    progressbar.pack()
    progressbar.start()
    nodoup()
    for n in nodo: 
        x,y =n
        nn = (x // 100)*10 + y//100
        hostip = '192.168.100.'+ str(nn)
        intface[hostip]=get_interfases(hostip)
    showint(n)
    progressbar.stop()
    print 'progress bar destryed'
    pb.destroy()

def show_values():
    global master,color
    delay,per_paq,per_bit = w1.get(),w2.get(),w3.get()
    color = 255-delay*220//1000,255-per_paq*220//100,255-per_bit* 220//1000
    label1.config(text = 'Delay =' +  str(delay))
    label2.config(text = 'Perdida de paquetes =' + str(per_paq))
    label3.config(text = 'Perdida de bits =' + str(per_bit)) 
    master.destroy()

    
def scaler():
    global w1,w2,w3,label1,label2,label3,master,delay,per_paq,per_bit
    master = Tk()
    master.title('Propiedades del enlace')
    w1 = Scale(master, from_=0, to=1000, tickinterval=500)
    w1.set(delay)
    w1.grid(row=0,column=0)
    label1 = Label(master)
    label1.config(text = 'Delay =' +  str(delay))
    label1.grid(row=1,column=0,padx=50)
    w2 = Scale(master, from_=0, to=100,tickinterval=50)
    w2.set(per_paq)
    w2.grid(row=0,column=1)
    label2 = Label(master)
    label2.config(text = 'Perdida de paquetes =' + str(per_paq))
    label2.grid(row=1,column=1,padx=50)
    w3 = Scale(master, from_=0, to=1000,tickinterval=500)
    w3.set(per_bit)
    w3.grid(row=0,column=2)
    label3 = Label(master,width=15)
    label3.config(text = 'Perdida de bits =' + str(per_bit))
    label3.grid(row=1,column=2,padx=50)
    Button(master, text='Set', command=show_values).grid(row=3,column=2)


def on_button3_release(event):
    global inicio,fin
    fin = near((event.x, event.y))
    if (fin[0] < 950 and fin[0] > 50) and (fin[1] < 950 and fin[1] > 50):
        if inicio==fin:
			if inicio in nodo:
				nodo.remove(inicio)
        else:
            linea=(inicio,fin)
            linear=(fin,inicio)
            link = [(i[0]) for i in link_color]
            if linea in link :
                i = link_color.pop(link.index(linea))
            elif linear in link:
                i = link_color.pop(link.index(linear))
    if run==1: ejecutar_enlace()
    dibujar()

def on_button_release(event):
    global inicio,fin
    fin = near((event.x, event.y))
    if fin[0] < 950 and fin[0] > 50 and fin[1] < 950 and fin[1] > 50:
        if inicio==fin:
            if inicio not in nodo: 
                nodo.append(inicio)
                current_nodo = inicio
        else:
            linea=(inicio,fin)
            linear=(fin,inicio)
            linea_color = (linea,color,pid)
            link = [(i[0]) for i in link_color]
            if inicio in nodo and fin in nodo:
                if linea not in link and linear not in link: 
                    link_color.append(linea_color)
                    if run==1:
                        ejecutar_enlace()   
    dibujar()

def borra_topo(): 
    global link_color,nodo
    if run == 0:
        link_color = []
        nodo = []   
    dibujar()

def ejecutar_script():
    global link_color,nodo,dir_trabajo, password,run
    for i in nodo:
        x1,y1 = i
        p=((x1 // 100)*10 + y1//100)
        p1 = str(p)
        p2 = str(p).zfill(2) 
        os.system('echo ' +password+' | sudo -S ip tuntap add tapwrt'+p1+' mode tap')
        os.system('echo ' +password+' | sudo -S ifconfig tapwrt'+p1+' inet 192.168.'+p1+'.1 up')
        os.system('vde_switch -d --hub -s /tmp/num'+p1+' -tap tapwrt'+p1+' -m 666 -f '+ dir_trabajo + '/colourful.rc')
        os.system('VBoxManage clonevm ' + v_name_base + ' --name num'+p1+' --register')
        os.system('VBoxManage modifyvm num'+p1+' --nic1 hostonly --hostonlyadapter1 vboxnet0 --macaddress1 8001000007'+ p2)
        os.system('VBoxManage modifyvm num'+p1+' --nic2 generic --nicgenericdrv2 VDE --nicproperty2 network=/tmp/num'+p1+'[2] --macaddress2 8002000007'+ p2)       
        os.system('VBoxManage modifyvm num'+p1+' --nic3 generic --nicgenericdrv3 VDE --nicproperty3 network=/tmp/num'+p1+'[3] --macaddress3 8003000007'+ p2)
        os.system('VBoxManage startvm num'+p1 +' --type headless') #--type headless
    os.system('echo ' +password+' | sudo -S ifconfig vboxnet0 inet 192.168.100.1 up')
    ejecutar_enlace()
    progresbar()
    run = 1	     
    
 
def ejecutar_wirefilter(i):
    global link_color
    linea,color,pid = i
    ((x1,y1),(x2,y2))=linea
    p1 = str((x1 // 100)*10 + y1//100)
    p2 = str((x2 // 100)*10 + y2//100)
    r=color[0]
    g=color[1]
    b=color[2]
    od ='wirefilter'+' --daemon -v /tmp/num'+ p1 +':/tmp/num' + p2	
    if r !=255 and r!=0:	od = od + ' -d ' + str(255-r) +'+'+ str((255-r)//2)
    if g !=255 and g!=0:	od = od + ' -l ' + str(255-g) 
    if b !=255 and b!=0:	od = od + ' -n ' + str(255-b)
    args = shlex.split(od)
    pp = subprocess.Popen(args)
    pid = pp.pid
    link_color.remove(i)
    link_color.append((linea,color,pid))


def ejecutar_enlace():
    global link_color
    os.system('killall wirefilter')
    for i in link_color[:]:
        ejecutar_wirefilter(i)
    dibujar()
      
def kill_script():	
    global run,nodo, password
    if run==1:
        os.system('echo ' +password+' | sudo -S killall -q wirefilter') 
        os.system('echo ' +password+' | sudo -S killall -q vde_switch') 
        for i in nodo:
            x1,y1 = i
            p1 = str((x1 // 100)*10 + y1//100)
            os.system('echo ' +password+' | sudo -S rm -rf /tmp/num' + p1)
            os.system('echo ' +password+' | sudo -S ip addr del 192.168.0.1' + p1 +'/24 dev tapwrt' +p1)
            os.system('echo ' +password+' | sudo -S ip link delete tapwrt' +p1)
            os.system('VBoxManage controlvm num' + p1 + ' poweroff')
            os.system('VBoxManage unregistervm --delete num' + p1 )
        os.system('echo ' +password+' | sudo -S ip addr del 192.168.100.1/24 dev vboxnet0')
        os.system('echo ' +password+' | sudo -S ip link set vboxnet0 down')
    run =0

def near(punto):
	x,y = punto
	xi,xd = divmod(x, 100)
	yi,yd = divmod(y, 100)
	if xd > 50:
		if xi < 10: xi =xi+1
	if yd > 50:
		yi =yi+1
	return xi*100,yi*100

def colorhex(r,g,b):
    return str('#'+'{:02x}'.format(r)+ '{:02x}'.format(g) + '{:02x}'.format(b))
    

def salir():
    global root,run
    if  run==1: kill_script()
    root.destroy()

def remover_enlaces():    
    global nodo,link_color
    for i in link_color[:]:	
		linea,color,pid = i
		((x1,y1),(x2,y2))=linea
		if (x1,y1) not  in nodo or (x2,y2) not in nodo: link_color.remove(i)
    dibujar()
					
def remover_nodos():
    global nodo,link_color
    link = [(j[0]) for j in link_color]	
    o = [(j[0]) for j in link]	
    d = [(j[1]) for j in link]	
    for i in nodo[:]:
		if i not in o and i not in d: nodo.remove(i)
    dibujar()

def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()
   
def sel():
    global b,varint,interfase
    interfase=varint.get()


def seleccionar_interfase():
    global varint,b,interfase
    b = Toplevel()
    b.title('Interfase')
    varint = IntVar()

    for text in curren_nodo_int_name:
        R1 = Radiobutton(b, text=text, variable=varint, value=curren_nodo_int_name.index(text)+1, command=sel)
        R1.pack( anchor = W )



root = Tk()
root.title('Simulador de redes Mesh')
w = Canvas(root, width=1000, height=1000)
w.pack()
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=select_dir)
filemenu.add_command(label="Open", command=open_list)
filemenu.add_command(label="Save", command=save_corriente)
filemenu.add_command(label="Save as...", command=save_list)
filemenu.add_command(label="Close", command=kill_script)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=salir)
menubar.add_cascade(label="File", menu=filemenu)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Remover topologia", command=borra_topo)
editmenu.add_command(label="Remover enlaces", command=remover_enlaces)
editmenu.add_command(label="Remover Nodos", command=remover_nodos)
editmenu.add_command(label="Propiedades del enlace", command=scaler)
menubar.add_cascade(label="Edit", menu=editmenu)

runmenu = Menu(menubar, tearoff=0)
runmenu.add_command(label="Ejecutar simulacion", command=ejecutar_script)
runmenu.add_command(label="Detener simulacion", command=kill_script)
menubar.add_cascade(label="Ejecutar", menu=runmenu)

snmpmenu = Menu(menubar, tearoff=0)
snmpmenu.add_command(label="Seleccionar Interfase",command=seleccionar_interfase)
menubar.add_cascade(label="SNMP", menu=snmpmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=progresbar)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
root.config(menu=menubar)
w.configure(background='black')
status = {}
intface ={}
nodo = []
link_color =[]
interfases=[]
interfase = 1
current_nodo = 0,0
curren_nodo_int =[]
curren_nodo_int_name =[]
inicio = 0,0
fin = 0,0
pid = 0
var = netsnmp.Varbind('iso.3.6.1.2.1.2.2.1.16.2') 
Rec = 'iso.3.6.1.2.1.2.2.1.11.'
Tran = 'iso.3.6.1.2.1.2.2.1.17.'
widthl = 1
dashl = [0]
delay = 0
per_paq = 0
per_bit = 0
run = 0
vms = 0
v_name_base= 'openwrt2i'
dir_trabajo = os.getcwd()
scrip_file =dir_trabajo +  '/geto.sh'
archivo_corriente =dir_trabajo + '/data'
color = 255-delay*220//1000,255-per_paq*220//100,255-per_bit* 220//1000
password = tkSimpleDialog.askstring('Ingrese password', 'password')
if os.path.isfile(archivo_corriente): 
    with open(archivo_corriente, 'rb') as f:
        nodo,link_color = pickle.load(f)

w.bind("<ButtonPress-1>", on_button_press)
w.bind("<ButtonRelease-1>",on_button_release)
w.bind("<ButtonPress-3>", on_button_press)
w.bind("<ButtonRelease-3>",on_button3_release)
root.after(1000,dibujar)
root.mainloop()
