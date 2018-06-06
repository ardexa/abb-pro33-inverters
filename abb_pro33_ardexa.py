"""
This script will query the PRO-33 ABB Inverter via Modbus RTU

Usage: abb_pro33_ardexa serial_device bus_address output_directory
eg:

Note: This plugin uses the modpoll tool.
    mkdir /opt/modpoll
    cd /opt/modpoll
    wget http://www.modbusdriver.com/downloads/modpoll.3.4.zip
    unzip modpoll.3.4.zip
    cd linux/
    chmod 755 modpoll
    sudo cp modpoll /usr/local/bin
"""

# Copyright (c) 2018 Ardexa Pty Ltd
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

from __future__ import print_function
import sys
import time
import os
from subprocess import Popen, PIPE
import click
import ardexaplugin as ap

PIDFILE = 'pro-33-ardexa.pid'
START_REG = "1"
REGS_TO_READ = "51"
BAUD_RATE = "19200"
PARITY = "none"

STATUS_DICT = {
    0:    "Connected",
    1400: "Regulatory delay",
    1300: "Grid synchronization",
    1200: "Connection tests",
    1100: "Grid unstable",
    1000: "Power-up tests",
    800:  "DC undervoltage",
    500:  "Active fault",
    300:  "Start inhibit active",
    200:  "Country code not set",
    100:  "Inverter disabled",
    1500: "Other",
    1150: "External trip signal",
    820:  "DC overvoltage"
}


def read_inverter(device, rtu_address, debug):
    """Attempt to contact the given bus address"""
    # initialise stdout and stderr to NULL
    stdout = ""
    stderr = ""
    errors = False
    register_dict = {}

    # This command is to get the parameter data from the inverters, minus the error codes
    # modpoll -m enc -a {rtu address} -r {start reg} -c {regs to read} -t 4:float -1 -4 10 -b {BAUD} {device}
    # Example: modpoll -a 1 -r 1 -c 51 -t 4 -1 -4 10 -b 19200 -p none /dev/ttyS0
    # pylint: disable=line-too-long
    ps = Popen(['modpoll',
                '-a', rtu_address,
                '-r', START_REG,
                '-c', REGS_TO_READ,
                '-t', '4',
                '-4', '10', '-1',
                '-p', PARITY,
                '-b', BAUD_RATE,
                device
               ],
               stdout=PIPE, stderr=PIPE)
    stdout, stderr = ps.communicate()

    # Modpoll will send the data to stderr, but also send errors on stderr as well. weird.
    if debug >= 2:
        print("STDOUT: ", stdout)
        print("STDERR: ", stderr)

    # for each line, split the register and return values
    for line in stdout.splitlines():
        # if the line starts with a '[', then process it
        if line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', '')
            register, value = line.split(':')
            register = register.strip()
            value = value.strip()
            register_dict[register] = value

    vac1 = vac2 = vac3 = vdc = idc = pac = cosphi = trip_fault = ""
    cb_temp = tempa = tempb = tempc = freq = total_energy = status = inv_on = ""
    idc_string1 = idc_string2 = idc_string3 = idc_string4 = ""
    idc_string5 = idc_string6 = idc_string7 = idc_string8 = ""


    count = 0
    # Get Parameters. If there are 0 parameters, then report an error
    # Otherwise accept the line
    if "47" in register_dict and "48" in register_dict:
        num2 = register_dict["47"]
        num1 = register_dict["48"]
        value, result = ap.convert_int32(num1, num2)
        if result:
            total_energy = value
            count += 1
    if "21" in register_dict and "22" in register_dict:
        num2 = register_dict["21"]
        num1 = register_dict["22"]
        value, result = ap.convert_int32(num1, num2)
        if result:
            status = value
            if status in STATUS_DICT:
                status = STATUS_DICT[status]
            count += 1
    if "12" in register_dict:
        trip_fault = register_dict["12"]
        count += 1
    if "1" in register_dict:
        inv_on = register_dict["1"]
        count += 1
    if "6" in register_dict:
        freq_raw = register_dict["6"]
        freq, result = ap.convert_to_float(freq_raw)
        if result:
            freq = freq / 100 # Divide by 100
            count += 1
    if "10" in register_dict:
        cosphi_raw = register_dict["10"]
        cosphi, result = ap.convert_to_float(cosphi_raw)
        if result:
            cosphi = cosphi / 100 # Divide by 100
            count += 1
    if "8" in register_dict:
        pac_raw = register_dict["8"]
        pac, result = ap.convert_to_float(pac_raw)
        if result:
            pac = pac * 100 # Multiply by 100 to get W
            count += 1
    if "4" in register_dict:
        vdc_raw = register_dict["4"]
        vdc, result = ap.convert_to_float(vdc_raw)
        if result:
            vdc = vdc / 10 ## Divide by 10 to get V
            count += 1
    if "11" in register_dict:
        idc_raw = register_dict["11"]
        idc, result = ap.convert_to_float(idc_raw)
        if result:
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
        idc_string1, result = ap.convert_to_float(idc_string1_raw)
        if result:
            idc_string1 = idc_string1 / 100 ## Divide by 100 to get A
            count += 1
    if "39" in register_dict:
        idc_string1_raw = register_dict["39"]
        idc_string1, result = ap.convert_to_float(idc_string1_raw)
        if result:
            idc_string1 = idc_string1 / 100 ## Divide by 100 to get A
            count += 1
    if "40" in register_dict:
        idc_string2_raw = register_dict["40"]
        idc_string2, result = ap.convert_to_float(idc_string2_raw)
        if result:
            idc_string2 = idc_string2 / 100 ## Divide by 100 to get A
            count += 1
    if "41" in register_dict:
        idc_string3_raw = register_dict["41"]
        idc_string3, result = ap.convert_to_float(idc_string3_raw)
        if result:
            idc_string3 = idc_string3 / 100 ## Divide by 100 to get A
            count += 1
    if "42" in register_dict:
        idc_string4_raw = register_dict["42"]
        idc_string4, result = ap.convert_to_float(idc_string4_raw)
        if result:
            idc_string4 = idc_string4 / 100 ## Divide by 100 to get A
            count += 1
    if "43" in register_dict:
        idc_string5_raw = register_dict["43"]
        idc_string5, result = ap.convert_to_float(idc_string5_raw)
        if result:
            idc_string5 = idc_string5 / 100 ## Divide by 100 to get A
            count += 1
    if "44" in register_dict:
        idc_string6_raw = register_dict["44"]
        idc_string6, result = ap.convert_to_float(idc_string6_raw)
        if result:
            idc_string6 = idc_string6 / 100 ## Divide by 100 to get A
            count += 1
    if "45" in register_dict:
        idc_string7_raw = register_dict["45"]
        idc_string7, result = ap.convert_to_float(idc_string7_raw)
        if result:
            idc_string7 = idc_string7 / 100 ## Divide by 100 to get A
            count += 1
    if "46" in register_dict:
        idc_string8_raw = register_dict["46"]
        idc_string8, result = ap.convert_to_float(idc_string8_raw)
        if result:
            idc_string8 = idc_string8 / 100 ## Divide by 100 to get A
            count += 1

    if count < 1:
        errors = True

    if debug > 0:
        print("For inverter at address: ", rtu_address)
        print("\tAC Voltage 1 (V): ", vac1)
        print("\tAC Voltage 2 (V): ", vac2)
        print("\tAC Voltage 3 (V): ", vac3)
        print("\tGrid Frequency (Hz): ", freq)
        print("\tAC Power (W): ", pac)
        print("\tPower Factor: ", cosphi)
        print("\tDC Voltage (V): ", vdc)
        print("\tDC Current (A): ", idc)
        print("\tInverter Temperature (C): ", cb_temp)
        print("\tTemperature A (C): ", tempa)
        print("\tTemperature B (C): ", tempb)
        print("\tTemperature C (C): ", tempc)
        print("\tEnergy today (kWh): ", total_energy)
        print("\tStatus: ", status)
        print("\tInverter ON: ", inv_on)
        print("\tTrip Fault: ", trip_fault)
        print("\tString Current 1 (A): ", idc_string1)
        print("\tString Current 2 (A): ", idc_string2)
        print("\tString Current 3 (A): ", idc_string3)
        print("\tString Current 4 (A): ", idc_string4)
        print("\tString Current 5 (A): ", idc_string5)
        print("\tString Current 6 (A): ", idc_string6)
        print("\tString Current 7 (A): ", idc_string7)
        print("\tString Current 8 (A): ", idc_string8)

    datetime = ap.get_datetime_str()

    header = "# Datetime, AC Voltage 1 (V), AC Voltage 2 (V), AC Voltage 3 (V), Grid Frequency (Hz), AC Power (W), Power Factor, DC Voltage (V), DC Current (A), Temperature 1 (C), Temperature 2 (C), Temperature 3 (C), Temperature 4 (C), Energy today (kWh), Status, Inverter ON, Trip Fault, String Current 1 (A), String Current 2 (A), String Current 3 (A), String Current 4 (A), String Current 5 (A), String Current 6 (A), String Current 7  (A),String Current 8 (A)\n"

    output_str = datetime + "," + ",".join(map(str, [vac1, vac2, vac3, freq, pac, cosphi, vdc, idc, cb_temp, tempa, tempb, tempc, total_energy, status, inv_on, trip_fault, idc_string1, idc_string2, idc_string3, idc_string4, idc_string5, idc_string6, idc_string7, idc_string8])) + "\n"

    # return the header and output
    return errors, header, output_str


#check the arguments
class Config(object):
    """Config object for click"""
    def __init__(self):
        self.verbosity = 0


CONFIG = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('-v', '--verbose', count=True)
@CONFIG
def cli(config, verbose):
    """Command line entry point"""
    config.verbosity = verbose


@cli.command()
@click.argument('serial_device')
@click.argument('bus_addresses')
@click.argument('output_directory')
@CONFIG
def log(config, serial_device, bus_addresses, output_directory):
    """Connect to the target serial device and log the inverter output for the given bus addresses"""
    # If the logging directory doesn't exist, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Check that no other scripts are running
    pidfile = os.path.join(output_directory, PIDFILE)
    if ap.check_pidfile(pidfile, config.verbosity):
        print("This script is already running")
        sys.exit(4)

    start_time = time.time()

    # For inverters, do the following
    for inverter_addr in ap.parse_address_list(bus_addresses):
        time.sleep(1) # ... wait between reads
        # First get the inverter parameter data
        errors, header_line, inverter_line = read_inverter(serial_device, str(inverter_addr), config.verbosity)
        if not errors:
            # Write the log entry, as a date entry in the log directory
            date_str = (time.strftime("%d-%b-%Y"))
            log_filename = date_str + ".csv"
            name = "inverter" + str(inverter_addr)
            log_directory_inv = os.path.join(output_directory, name)
            ap.write_log(log_directory_inv, log_filename, header_line, inverter_line, config.verbosity, True, log_directory_inv, "latest.csv")


    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")

    # Remove the PID file
    if os.path.isfile(pidfile):
        os.unlink(pidfile)
