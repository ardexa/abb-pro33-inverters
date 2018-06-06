
# Purpose
ABB (http://www.abb.com/) supply retail and commercial grade Solar PV inverters. The purpose of this project is to collect data from ABB PRO-33 Inverters and send the data to your cloud using Ardexa. Data from ABB PRO-33 solar inverters is read using an RS485 connection to the inverters and a Linux device such as a Raspberry Pi, or an X86 intel powered computer. 

## How does it work
This application is written in Python, to query PRO-33 inverters connected via RS485. This application will query 1 or more connected inverters at regular intervals. Data will be written to log files on disk in a directory specified by the user. Usage and command line parameters are as follows:

Usage: sudo python pro-33-ardexa.py {serial device} {start address} {end address} {log directory} {debug type}, where...
- {serial device} = ..something like: /dev/ttyS0
- {start addresses} = an RS485 start address (eg; 1-32)
- {end addresses} = an RS485 end address (eg; 1-32)
- {log directory} = the logging directory
- {debug type} = 0 (no messages, except errors), 1 (discovery messages) or 2 (all messages)
- eg: sudo python pro-33-ardexa.py /dev/ttyS0 1 8 /opt/ardexa 1

# ABB PRO-33 Inverter
ABB’s three-phase PRO-33.0 string inverter is available in 33 kW and is designed for medium and large de-centralized PV systems either on large-scale commercial and industrial rooftops or ground-mounted PV plants up to megawatt (MW) sizes. It is marketed by ABB. This plugin reads from these inverters, using the inbuilt Modbus RTU Protocol. Please take a look at the 'docs' directory for discussion of the implementation of the Modbus RTU protocol for the ABB PRO-33 Inverter.

Remember these things:
1. Connection from your Linux device to the first inverter is via RS485 daisy chain.
2. Each inverter (if there are more than 1) must have a UNIQUE RS485 address

If in doubt, see the latest documentation on the ABB website.

## How to use the script
On a raspberry Pi, or other Linux machines (arm, intel, mips or whatever), make sure Python is installed (which it should be). Then install the dependancy as follows:

```
mkdir /opt/modpoll
cd /opt/modpoll
wget http://www.modbusdriver.com/downloads/modpoll.3.4.zip
unzip modpoll.3.4.zip 
cd linux/
chmod 755 modpoll 
sudo cp modpoll /usr/local/bin
```

Then install and run this project as follows:
Note that the applications should be run as root.
```
cd
git https://github.com/ardexa/abb-pro33-inverters.git
cd abb-pro33-inverters
Usage: sudo python pro-33-ardexa.py {serial device} {start address} {end address} {log directory} {debug type}
eg: sudo python pro-33-ardexa.py /dev/ttyS0 1 8 /opt/ardexa 1
```

## Collecting to the Ardexa cloud
Collecting to the Ardexa cloud is free for up to 3 Raspberry Pis (or equivalent). Ardexa provides free agents for ARM, Intel x86 and MIPS based processors. To collect the data to the Ardexa cloud do the following:
- Create a `RUN` scenario to schedule the Ardexa ABB Pro 33 script to run at regular intervals (say every 300 seconds/5 minutes).
- Then use a `CAPTURE` scenario to collect the csv (comma separated) data from the filename (say) `/opt/ardexa/pro33/inverter1/logs/`. This file contains a header entry (as the first line) that describes the CSV elements of the file.

## Help
Contact Ardexa at support@ardexa.com, and we'll do our best efforts to help.


 

