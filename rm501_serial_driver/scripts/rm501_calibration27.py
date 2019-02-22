#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
from roboclaw27 import Roboclaw

#Windows comport name
#rc = Roboclaw("COM3",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyUSB0",115200)

def displayspeed():
	enc0 = rc.ReadEncM1(address1)
	enc1 = rc.ReadEncM2(address1)
	enc2 = rc.ReadEncM1(address2)
	enc3 = rc.ReadEncM2(address2)
	enc4 = rc.ReadEncM1(address3)
	enc5 = rc.ReadEncM2(address3)


	speed1 = rc.ReadSpeedM1(address1)
	speed2 = rc.ReadSpeedM2(address1)

	print("\n Encoder1:"),
	if(enc1[0]==1):
		print enc1[1],
		print format(enc1[2],'02x'),
	else:
		print "failed",
	print "Encoder2:",
	if(enc2[0]==1):
		print enc2[1],
		print format(enc2[2],'02x'),
	else:
		print "failed " ,
	print("Encoder3:"),
	if(enc3[0]==1):
		print enc3[1],
		print format(enc3[2],'02x'),
	else:
		print "failed",
	print "Encoder4:",
	if(enc4[0]==1):
		print enc4[1],
		print format(enc4[2],'02x'),
	else:
		print "failed " ,
	print("Encoder5:"),
	if(enc5[0]==1):
		print enc5[1],
		print format(enc5[2],'02x'),
	else:
		print "failed"

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
		time.sleep(4)
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
		time.sleep(4)
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


#homeaxis(address1,1)
homeaxis(address1,2,3000,25)
homeaxis(address2,1,2000,5)
homeaxis(address2,2,2000,10)
rc.SetEncM1(address3,0)
rc.SetEncM2(address3,0)

# GRIPPER open

rc.SpeedM1(address1,-800)
time.sleep(1)
rc.SpeedM1(address1,0)

rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,24000,100)
time.sleep(0.5)
rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,2500,100)
time.sleep(0.5)
rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,14500,100)
time.sleep(0.5)

#Stop motors
#rc.DutyM1M2(address1,0,0)
#rc.DutyM1M2(address2,0,0)
#rc.DutyM1M2(address3,0,0)

while(1):


	for i in range(0,20):
		displayspeed()
		time.sleep(0.01)

  
