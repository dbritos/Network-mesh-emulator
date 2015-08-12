#!/bin/sh
unzip master.zip
apt-get install libsdl1.2debian
wget -c http://download.virtualbox.org/virtualbox/5.0.0/virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb
dpkg --install virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb
apt-get install snmp
tar -xf vde2-2.3.2-patch.tar
cd vde2-2.3.2-patch
./configure 
make
makeinstall
cd ..
apt-get install libvdeplug2
apt-get install python2.7
apt-get install python-gtk2-dev
apt-get install python-gobject
apt-get install python-cairo
apt-get install python-netsnmp
VBoxManage import openwrtv12.ova
