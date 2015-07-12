Network Mesh emulator
=====================

This is a network Mesh emulator with batman-adv. Is written in python and work with Virtualbox and vde-switch.

####Key features:

- Its possible to build topologies to 81 nodes.
- Each node can be a different virtual machine.
- Compatibility with Wireshark.
- Its possible change the links properties while the emulation is running.
- Easy access to each virtual machine.

####Prerequisites

- Linux (developed on Ubuntu 14.08)
- Python 2.7
- VirtualBox.
- OpenWrt.
- vde-switch.
- vde_switch colour patch.
- python library pygtk, gobject, cairo,math, pickle os, netsnmp, time and vboxapi.

####Installation

1. Install all of the necessary Python modules listed above. Many of them are available via pip and/or apt-get.
2. Install Virtualbox.
3. Add a Host-only Network (vboxnet0) in Virtualbox -> Preferences -> Network 
4. Install vde_switch with the patch.
5. Import the provided OpenWrt virtual machine (openwrt.ova).
6. Run the program $>python simmeshv11.py

####Basic usage

Read the wiki Emulator Manual.

####Example.

In this example one can view five networks of nine nodes each one with links in 2.4 GHz band and connected the five network with links of 5.0 GHz Band.

![Example](https://github.com/dbritos/Network-mesh-emulator/blob/master/figures/example.png "Example")

In the right  of the screen there are the originators and next hope list for the node number 66.

In the next figure is shown the node 66 making a ping to node number 11, the times are good.

![Ping](https://github.com/dbritos/Network-mesh-emulator/blob/master/figures/ping.png "ping")

In the last figure is shown the cpu and memory usage for 36 nodes running together.

![CPU usage](https://github.com/dbritos/Network-mesh-emulator/blob/master/figures/Untitled.png "cpu usage")
