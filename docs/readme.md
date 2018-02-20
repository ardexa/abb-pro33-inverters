

## Documents
- https://ardexa.app.box.com/file/277458010410
- https://ardexa.app.box.com/file/268395674405
A. EN_PRO-33.0-TL_Service_Menu_Guide_C_A4.pdf ... page 103


## Modbus Map
- Uses `holding registers`

- Command: modpoll -r 1 -c 51 -t 4 -1 -4 10 -b 19200 -p none /dev/ttyS0
- Note document says Modbus starts at 0. But modpoll starts at 1
- Output from `modpoll`

1: Inverter Status: 0 = Inverter disabled ; 1 = Inverter enabled
4: DC Voltage ... divide by 10 to get V
6: Grid Frequency ... divide by 100 to get Hz
8: AC Power ... divide by 10 to get kW. 
10. Cos phi. divide by 100. check value
11. DC Current ... don't use #4 (its calculated). Divide by 10 to get A
12. is a 'tripping fault'. "...Fault which actually caused the inverter to trip,"
21: (32 bit) .. connection status. Use 172.01 Page 74 of Ref A to convert to keyword
35: Control board temperature  ...  no conversion required
36: Inverter temperature A  ...  no conversion required
37: Inverter temperature B  ...  no conversion required
38: Inverter temperature C  ...  no conversion required

39: 	String Current 1 .... but check ...divide by 100 to get A
40: 	String Current 2 .... but check ...divide by 100 to get A
41: 	String Current 3 .... but check ...divide by 100 to get A
42: 	String Current 4 .... but check ...divide by 100 to get A
43: 	String Current 5 .... but check ...divide by 100 to get A
44: 	String Current 6 .... but check ...divide by 100 to get A
45: 	String Current 7 .... but check ...divide by 100 to get A
46: 	String Current 8 .... but check ...divide by 100 to get A

47+48: Total Energy (kWh)...but note. its 32 bit
49: AC Voltage 1 ...  no conversion required
50: AC Voltage 2 ...  no conversion required
51: AC Voltage 3 ...  no conversion required


- Notes; 4+5 = DC Voltage and Current. See to be just above AC Power (8).
- 39-46 currents add up to to 4 (DC Current)



