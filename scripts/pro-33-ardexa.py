#! /usr/bin/python

# Copyright (c) 2013-2018 Ardexa Pty Ltd
#
# This code is licensed under the MIT License (MIT).
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# This script will query the PRO-33 ABB Inverter via Modbus RTU 
#
# Usage: python pro-33-ardexa.py device start_address end_address log_directory query_type debug_str
# eg: 
#
# Note: This plugin uses the modpoll tool.
# 		mkdir /opt/modpoll
#		cd /opt/modpoll
#		wget http://www.modbusdriver.com/downloads/modpoll.3.4.zip
#		unzip modpoll.3.4.zip 
#		cd linux/
#		chmod 755 modpoll 
#		sudo cp modpoll /usr/local/bin
#

import sys
import time
import os
from Supporting import *
from subprocess import Popen, PIPE, STDOUT

PIDFILE = 'pro-33-ardexa.pid'
START_REG = "1"
REGS_TO_READ = "51"
BAUD_RATE = "19200"
PARITY = "none"

status_dict = { 0 : "Connected", 1400: "Regulatory delay", 1300 : "Grid synchronization" , 1200 : "Connection tests" , 1100 : "Grid unstable", 1000 : "Power-up tests" , 800 : "DC undervoltage" , 500 : "Active fault", 300 : "Start inhibit active" , 200 : "Country code not set" , 100: "Inverter disabled" , 1500 : "Other", 1150: "External trip signal", 820: "DC overvoltage" }


#~~~~~~~~~~~~~~~~~~~   START Functions ~~~~~~~~~~~~~~~~~~~~~~~

def read_inverter(device, rtu_address, debug):
	# initialise stdout and stderr to NULL
	stdout = ""
	stderr = ""
	errors = False
	register_dict = {}

	# This command is to get the parameter data from the inverters, minus the error codes
	# modpoll -m enc -a {rtu address} -r {start reg} -c {regs to read} -t 4:float -1 -4 10 -b {BAUD} {device}
	# Example: modpoll -a 1 -r 1 -c 51 -t 4 -1 -4 10 -b 19200 -p none /dev/ttyS0
	ps = Popen(['modpoll', '-a', rtu_address, '-r', START_REG, '-c', REGS_TO_READ, '-t', '4', '-4', '10', '-1', '-p', PARITY, '-b', BAUD_RATE, device], stdout=PIPE, stderr=PIPE)
	stdout, stderr  = ps.communicate()
		
	# Modpoll will send the data to stderr, but also send errors on stderr as well. weird.
	if (debug >= 2):
		print "STDOUT: ", stdout
		print "STDERR: ", stderr

	# for each line, split the register and return values
	for line in stdout.splitlines():
		# if the line starts with a '[', then process it
		if (line.startswith('[')):
			line = line.replace('[','')	
			line = line.replace(']','')	
			register,value = line.split(':')
			register = register.strip()
			value = value.strip()
			register_dict[register] = value

	vac1 = vac2 = vac3 = vdc = idc = pac = cosphi = trip_fault =""
	cb_temp = tempa = tempb = tempc = freq = total_energy = status = inv_on = ""
	idc_string1 = idc_string2 = idc_string3 = idc_string4 = idc_string5 = idc_string6 = idc_string7 = idc_string8 = ""


	count = 0
	# Get Parameters. If there are 0 parameters, then report an error
	# Otherwise accept the line
	if (("47" in register_dict) and (("48" in register_dict))):
		num2 = register_dict["47"]
		num1 = register_dict["48"]
		result, value = convert_32(num1, num2)
		if (result):
			total_energy = value	
			count += 1
	if (("21" in register_dict) and (("22" in register_dict))):
		num2 = register_dict["21"]
		num1 = register_dict["22"]
		result, value = convert_32(num1, num2)   
		if (result):
			status = value	
			if status in status_dict:
				status = status_dict[status]
			count += 1
	if "12" in register_dict:
		trip_fault = register_dict["12"]
		count += 1
	if "1" in register_dict:
		inv_on = register_dict["1"]
		count += 1
	if "6" in register_dict:
		freq_raw = register_dict["6"]
		result, freq = convert_to_float(freq_raw)
		if (result):
			freq = freq / 100 # Divide by 100
			count += 1
	if "10" in register_dict:
		cosphi_raw = register_dict["10"]
		result, cosphi = convert_to_float(cosphi_raw)
		if (result):
			cosphi = cosphi / 100 # Divide by 100
			count += 1
	if "8" in register_dict:
		pac_raw = register_dict["8"]
		result, pac = convert_to_float(pac_raw)
		if (result):
			pac = pac * 100 # Multiply by 100 to get W
			count += 1
	if "4" in register_dict:
		vdc_raw = register_dict["4"]
		result, vdc = convert_to_float(vdc_raw)
		if (result):
			vdc = vdc / 10 ## Divide by 10 to get V
			count += 1
	if "11" in register_dict:
		idc_raw = register_dict["11"]
		result, idc = convert_to_float(idc_raw)
		if (result):
			idc = idc / 10 ## Divide by 10 to get A
			count += 1
	if "35" in register_dict:
		cb_temp = register_dict["35"]
		count += 1
	if "36" in register_dict:
		tempa = register_dict["36"]
		count += 1
	if "37" in register_dict:
		tempb = register_dict["37"]
		count += 1
	if "38" in register_dict:
		tempc = register_dict["38"]
		count += 1
	if "49" in register_dict:
		vac1 = register_dict["49"]
		count += 1
	if "50" in register_dict:
		vac2 = register_dict["50"]
		count += 1
	if "51" in register_dict:
		vac3 = register_dict["51"]
		count += 1
	if "39" in register_dict:
		idc_string1_raw = register_dict["39"]
		result, idc_string1 = convert_to_float(idc_string1_raw)
		if (result):
			idc_string1 = idc_string1 / 100 ## Divide by 100 to get A
			count += 1
	if "39" in register_dict:
		idc_string1_raw = register_dict["39"]
		result, idc_string1 = convert_to_float(idc_string1_raw)
		if (result):
			idc_string1 = idc_string1 / 100 ## Divide by 100 to get A
			count += 1
	if "40" in register_dict:
		idc_string2_raw = register_dict["40"]
		result, idc_string2 = convert_to_float(idc_string2_raw)
		if (result):
			idc_string2 = idc_string2 / 100 ## Divide by 100 to get A
			count += 1
	if "41" in register_dict:
		idc_string3_raw = register_dict["41"]
		result, idc_string3 = convert_to_float(idc_string3_raw)
		if (result):
			idc_string3 = idc_string3 / 100 ## Divide by 100 to get A
			count += 1
	if "42" in register_dict:
		idc_string4_raw = register_dict["42"]
		result, idc_string4 = convert_to_float(idc_string4_raw)
		if (result):
			idc_string4 = idc_string4 / 100 ## Divide by 100 to get A
			count += 1
	if "43" in register_dict:
		idc_string5_raw = register_dict["43"]
		result, idc_string5 = convert_to_float(idc_string5_raw)
		if (result):
			idc_string5 = idc_string5 / 100 ## Divide by 100 to get A
			count += 1
	if "44" in register_dict:
		idc_string6_raw = register_dict["44"]
		result, idc_string6 = convert_to_float(idc_string6_raw)
		if (result):
			idc_string6 = idc_string6 / 100 ## Divide by 100 to get A
			count += 1
	if "45" in register_dict:
		idc_string7_raw = register_dict["45"]
		result, idc_string7 = convert_to_float(idc_string7_raw)
		if (result):
			idc_string7 = idc_string7 / 100 ## Divide by 100 to get A
			count += 1
	if "46" in register_dict:
		idc_string8_raw = register_dict["46"]
		result, idc_string8 = convert_to_float(idc_string8_raw)
		if (result):
			idc_string8 = idc_string8 / 100 ## Divide by 100 to get A
			count += 1

	if (count < 1):
		errors = True

	if (debug > 0):
		print "For inverter at address: ", rtu_address
		print "\tAC Voltage 1 (V): ", vac1
		print "\tAC Voltage 2 (V): ", vac2
		print "\tAC Voltage 3 (V): ", vac3
		print "\tGrid Frequency (Hz): ", freq
		print "\tAC Power (W): ", pac
		print "\tPower Factor: ", cosphi
		print "\tDC Voltage (V): ", vdc
		print "\tDC Current (A): ", idc
		print "\tInverter Temperature (C): ", cb_temp
		print "\tTemperature A (C): ", tempa
		print "\tTemperature B (C): ", tempb
		print "\tTemperature C (C): ", tempc
		print "\tEnergy today (kWh): ", total_energy 
		print "\tStatus: ", status
		print "\tInverter ON: ", inv_on
		print "\tTrip Fault: ", trip_fault
		print "\tString Current 1 (A): ", idc_string1
		print "\tString Current 2 (A): ", idc_string2
		print "\tString Current 3 (A): ", idc_string3
		print "\tString Current 4 (A): ", idc_string4
		print "\tString Current 5 (A): ", idc_string5
		print "\tString Current 6 (A): ", idc_string6
		print "\tString Current 7 (A): ", idc_string7
		print "\tString Current 8 (A): ", idc_string8

	datetime_str = get_datetime()

	header = "# Datetime, AC Voltage 1 (V), AC Voltage 2 (V), AC Voltage 3 (V), Grid Frequency (Hz), AC Power (W), Power Factor, DC Voltage (V), DC Current (A), Temperature 1 (C), Temperature 2 (C), Temperature 3 (C), Temperature 4 (C), Energy today (kWh), Status, Inverter ON, Trip Fault, String Current 1 (A), String Current 2 (A), String Current 3 (A), String Current 4 (A), String Current 5 (A), String Current 6 (A), String Current 7  (A),String Current 8 (A)\n"
	
	output_str =  datetime_str + "," +  str(vac1) + "," + str(vac2) + "," + str(vac3) + "," + str(freq) + "," + str(pac) + "," + str(cosphi) + "," + str(vdc) + "," + str(idc) + "," + str(cb_temp) + "," + str(tempa) + "," + str(tempb) + "," + str(tempc) + "," + str(total_energy) + "," + str(status) + "," + str(inv_on) + "," + str(trip_fault) + str(idc_string1) + "," + str(idc_string2) + "," + str(idc_string3) + "," + str(idc_string4) + "," + str(idc_string5) + "," + str(idc_string6) + "," + str(idc_string7) + "," + str(idc_string8) + "\n"

	# return the header and output
	return errors, header, output_str




# This function converts 2 binary 16 bit numbers to a 32 bit signed integer
def convert_32(num1_str, num2_str):
	try:
		num1_bin = bin(int(num1_str))[2:]
		num2_bin = bin(int(num2_str))[2:]
		res = num1_bin + num2_bin
		number = int(res, 2)
		full_int = pow(2,32)
		if (number > (full_int/2)):
			number = number - full_int
		return True, number
	except:
		return False, ""

#~~~~~~~~~~~~~~~~~~~   END Functions ~~~~~~~~~~~~~~~~~~~~~~~

# Check script is run as root
if os.geteuid() != 0:
	print "You need to have root privileges to run this script, or as \'sudo\'. Exiting."
	sys.exit(1)

#check the arguments
arguments = check_args(5)
if (len(arguments) < 5):
	print "The arguments cannot be empty. Usage: ", USAGE
	sys.exit(2)

device = arguments[1]
start_address = arguments[2]
end_address = arguments[3]
log_directory = arguments[4]
debug_str = arguments[5]

# Convert debug
retval, debug = convert_to_int(debug_str)
if (not retval):
	print "Debug needs to be an integer number. Value entered: ",debug_str
	sys.exit(3)

# If the logging directory doesn't exist, create it
if (not os.path.exists(log_directory)):
	os.makedirs(log_directory)

# Check that no other scripts are running
pidfile = os.path.join(log_directory, PIDFILE)
if check_pidfile(pidfile, debug):
	print "This script is already running"
	sys.exit(4)

# If any args are empty, exit with error
if ((not device) or (not start_address) or (not end_address) or (not log_directory)):
	print "The arguments cannot be empty. Usage: ", USAGE
	sys.exit(5)

# Convert start and stop addresses
retval_start, start_addr = convert_to_int(start_address)
retval_end, end_addr = convert_to_int(end_address)
if ((not retval_start) or (not retval_end)):
	print "Start and End Addresses need to be an integers"
	sys.exit(6)

start_time = time.time()

# For inverters, do the following
for rtu_address in range(start_addr, (end_addr + 1)):
	time.sleep(1) # ... wait between reads
	# First get the inverter parameter data
	errors, header_line, inverter_line = read_inverter(device, str(rtu_address), debug)
	if (not errors):
		# Write the log entry, as a date entry in the log directory
		date_str = (time.strftime("%d-%b-%Y"))
		log_filename = date_str + ".csv"
		name = "inverter" + str(rtu_address)
		log_directory_inv = os.path.join(log_directory, name)
		write_log(log_directory_inv, log_filename, header_line, inverter_line, debug, True, log_directory_inv, "latest.csv")


elapsed_time = time.time() - start_time
if (debug > 0):
	print "This request took: ",elapsed_time, " seconds."

# Remove the PID file	
if os.path.isfile(pidfile):
	os.unlink(pidfile)

print 0

