#!/bin/sh
file="virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb"
if [ -e ${PWD}/$file ];
then echo "existe"   ${PWD}/$file
else wget -c http://download.virtualbox.org/virtualbox/5.0.0/virtualbox-5.0_5.0.0-101573~Ubuntu~trusty_amd64.deb	
fi
apt-get -y install libsdl1.2debian
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
apt-get -y remove libvdeplug2
apt-get -y install libvdeplug2
VBoxManage import openwrtv12.ova


