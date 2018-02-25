

## Documents
A. EN_PRO-33.0-TL_Service_Menu_Guide_C_A4.pdf ... page 103


## Modbus Map
- Uses `holding registers`
- Command: modpoll -r 1 -c 51 -t 4 -1 -4 10 -b 19200 -p none /dev/ttyS0
- Note document says Modbus starts at 0. But modpoll starts at 1

Register		Name									Notes
1				Inverter Status					0 = Inverter disabled ; 1 = Inverter enabled
4				DC Voltage							divide by 10 to get V
6				Grid Frequency						divide by 100 to get Hz
8				AC Power								divide by 10 to get kW. 
10				Cos phi								divide by 100
11				DC Current							don't use Register 4 (its calculated). Divide by 10 to get A
12				Trip Fault							this is a 'tripping fault'. "...Fault which actually caused the inverter to trip,"
21 			Connection status					Use 172.01 Page 74 of Ref A to convert to keyword
35				Control board temperature		no conversion required
36				Inverter temperature A 			no conversion required
37				Inverter temperature B			no conversion required
38				Inverter temperature C			no conversion required
39				String Current 1					divide by 100 to get A
40				String Current 2					divide by 100 to get A
41				String Current 3					divide by 100 to get A
42				String Current 4					divide by 100 to get A
43				String Current 5					divide by 100 to get A
44				String Current 6					divide by 100 to get A
45				String Current 7					divide by 100 to get A
46				String Current 8					divide by 100 to get A
47+48			Total Energy (kWh)				32 bit
49				AC Voltage 1						no conversion required
50				AC Voltage 2						no conversion required
51				AC Voltage 3						no conversion required


