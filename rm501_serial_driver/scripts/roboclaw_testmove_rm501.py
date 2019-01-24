#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000
import time
from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM3",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyUSB0",115200)


DEFAULT_MINLIM4 = 0
DEFAULT_MAXLIM4 = 180
DEFAULT_MINLIM5 = -180
DEFAULT_MAXLIM5 = 180
DEFAULT_COUNTRAD1 =106
DEFAULT_COUNTRAD2 =106
DEFAULT_COUNTRAD3 =106
DEFAULT_COUNTRAD4 =106
DEFAULT_COUNTRAD5 =106


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

def movedifftrans(address,posM1ang,posM2ang):
#reduction grad to counts
		
	reduction1=DEFAULT_COUNTRAD4
	reduction2=DEFAULT_COUNTRAD5

	posM1=reduction1*(posM1ang + posM2ang)
	posM2=reduction2*(posM1ang - posM2ang)

	rc.SpeedAccelDeccelPositionM1(address,3000,10000,10000,posM1,100)
	rc.SpeedAccelDeccelPositionM2(address,3000,10000,10000,posM2,100)

def movenormtrans(address,posM1ang,posM2ang,reduction1,reduction2):
#reduction grad to counts

	posM1=reduction1*posM1ang
	posM2=reduction2*posM2ang

	rc.SpeedAccelDeccelPositionM1(address,3000,10000,10000,posM1,100)
	rc.SpeedAccelDeccelPositionM2(address,3000,10000,10000,posM2,100)



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
	

	rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,39000,100)
	rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,12000,100)
	rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,5000,100)
	movedifftrans(address3,30,0)
	time.sleep(4)

	rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,39000,100)
	rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,13000,100)
	rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,6000,100)
	movedifftrans(address3,30,0)
	time.sleep(1)


	rc.SpeedM1(address1,50)
	time.sleep(3)

	rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,24000,100)
	rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,2500,100)
	rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,14500,100)
	movedifftrans(address3,90,-180)
	time.sleep(4)

	rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,39000,100)
	rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,12000,100)
	rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,5000,100)
	movedifftrans(address3,30,0)
	time.sleep(5)

	rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,39000,100)
	rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,13000,100)
	rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,6000,100)
	movedifftrans(address3,30,0)
	time.sleep(1)


	rc.SpeedM1(address1,-50)
	time.sleep(2)

	rc.SpeedAccelDeccelPositionM2(address1,2000,10000,10000,24000,100)
	rc.SpeedAccelDeccelPositionM1(address2,2000,10000,10000,2500,100)
	rc.SpeedAccelDeccelPositionM2(address2,2000,10000,10000,14500,100)
	movedifftrans(address3,90,-180)


	for i in range(0,20):
		displayspeed()
		time.sleep(0.01)
  
