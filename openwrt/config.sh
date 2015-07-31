#!/bin/sh
route add default gw $1
echo "nameserver" $1>/etc/resolv.conf
#install packages
opkg update
opkg install kernel 
opkg install snmpd 
opkg install ip 
opkg install kmod-batman-adv
opkg install batctl
cp ./rc.local /etc/rc.local
#Enable SNMP daemon
/etc/init.d/snmpd restart
 echo 'Configuring and starting snmpd'

uci delete snmpd.private
uci delete snmpd.public
uci commit snmpd

uci set snmpd.@agent[0].agentaddress='UDP:161,UDP6:161'
uci add snmpd public
uci set snmpd.public=com2sec
uci set snmpd.public.secname=rw
uci set snmpd.public.source=192.168.0.0/16
uci set snmpd.public.community=public
uci commit snmpd
uci add snmpd private
uci set snmpd.private=com2sec
uci set snmpd.private.secname=rw
uci set snmpd.private.source=192.168.0.0/16
uci set snmpd.private.community=private
uci commit snmpd
uci add snmpd com2sec6
uci set snmpd.@com2sec6[-1].secname=rw
uci set snmpd.@com2sec6[-1].source=default
uci set snmpd.@com2sec6[-1].community=public
uci commit snmpd
uci add snmpd com2sec6
uci set snmpd.@com2sec6[-1].secname=rw
uci set snmpd.@com2sec6[-1].source=default
uci set snmpd.@com2sec6[-1].community=private
uci commit snmpd

uci add snmpd pass
uci set snmpd.@pass[-1].miboid=.1.3.6.1.4.1.32.1.1
uci set snmpd.@pass[-1].prog=/root/snmp/batctl_o.sh
uci commit snmpd
uci add snmpd pass
uci set snmpd.@pass[-1].miboid=.1.3.6.1.4.1.32.1.2
uci set snmpd.@pass[-1].prog=/root/snmp/batctl_n.sh
uci commit snmpd
uci add snmpd pass
uci set snmpd.@pass[-1].miboid=.1.3.6.1.4.1.32.1.3
uci set snmpd.@pass[-1].prog=/root/snmp/batctl_tg.sh
uci commit snmpd
uci add snmpd pass
uci set snmpd.@pass[-1].miboid=.1.3.6.1.4.1.32.1.4
uci set snmpd.@pass[-1].prog=/root/snmp/batctl_tr.sh
uci commit snmpd
/etc/init.d/snmpd restart  
/etc/init.d/snmpd enable      
/etc/init.d/snmpd restart

