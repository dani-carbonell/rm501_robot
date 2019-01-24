import time
from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM9",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyUSB1",38400)

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
	displayspeed()
