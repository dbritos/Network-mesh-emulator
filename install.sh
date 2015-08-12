#!/bin/sh
wget -c https://github.com/dbritos/Network-mesh-emulator/blob/master/openwrtv12.ova
wget -c https://github.com/dbritos/Network-mesh-emulator/blob/master/simmeshv12.py
wget https://github.com/dbritos/Network-mesh-emulator/blob/master/vde2-2.3.2-patch.tar
sudo apt-get install virtualbox
tar -xf vde2-2.3.2-patch.tar
cd vde2-2.3.2-patch
configure 
make
makeinstall
apt-get install python2.7
apt-get install python-gtk2-dev
apt-get install python-gobject
apt-get install python-cairo
apt-get install python-netsnmp
VBoxManage import openwrtv12.ova --vmname openwrtv12 --memory 32
