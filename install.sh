make#!/bin/sh
apt-get -y install libsdl1.2debian
if [! -f virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb ];
then
   wget -c http://download.virtualbox.org/virtualbox/5.0.0/virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb	
fi
dpkg --install virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb
apt-get -y install snmp
tar -xf vde2-2.3.2-patch.tar
cd vde2-2.3.2-patch
./configure 
make
make install
cd ..
apt-get -y install libvdeplug2
apt-get -y install python2.7
apt-get -y install python-gtk2-dev
apt-get -y install python-gobject
apt-get -y install python-cairo
apt-get -y install python-netsnmp
VBoxManage import openwrtv12.ova
