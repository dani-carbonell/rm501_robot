#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM3",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyUSB0",115200)



def homeaxis(address,motorN,speed,caltime):
	
	if (motorN == 1):
		#Move the axis away from to the homing switch to make sure we are not pressing it when the calibration starts.
		rc.SetEncM1(address,500000)				
		rc.SpeedM1(address,80)
		time.sleep(0.5)	
		rc.SpeedM1(address,-speed)
		for i in range(0,caltime):
			if (rc.ReadEncM1(address)[1]>10):
				time.sleep(1)
		rc.SpeedM1(address,speed)
		time.sleep(0.1)
		#Fine homing		
		rc.SpeedM1(address,-100)
		time.sleep(3)
		rc.SpeedM1(address,0)
	
	else:
		#Move the axis away from to the homing switch to make sure we are not pressing it when the calibration starts.
		rc.SetEncM2(address,500000)				
		rc.SpeedM2(address,80)
		time.sleep(0.5)	
		rc.SpeedM2(address,-speed)
		for i in range(0,caltime):
			if (rc.ReadEncM2(address)[1]>10):
				time.sleep(1)
		rc.SpeedM2(address,speed)
		time.sleep(0.1)
		#Fine homing		
		#Fine homing		
		rc.SpeedM2(address,-100)
		time.sleep(3)
		rc.SpeedM2(address,0)


rc.Open()
address1 = 0x80
address2 = 0x81
address3 = 0x82

version1 = rc.ReadVersion(address1)
version2 = rc.ReadVersion(address2)
version3 = rc.ReadVersion(address3)

if version1[0]==False:
	print "GETVERSION Failed"
else:
	print repr(version1[1])
	print repr(version2[1])
	print repr(version3[1])



while(1):


	for i in range(0,20):
		rc.SpeedM1(address1,32767)
		time.sleep(2)
		rc.SpeedM1(address1,-32767)
		time.sleep(2)  
