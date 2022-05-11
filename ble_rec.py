import socket
from struct import unpack
from ahrs import DCM, QuaternionArray
from ahrs.filters import Madgwick
import numpy
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 1969))

'''
mag = Madgwick()
while True:
	data, addr = sock.recvfrom(1024)

	acc = [unpack('<f', data[2:6])[0], unpack('<f', data[6: 10])[0], unpack('<f', data[10: 14])[0]]
	gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
	quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
	pyr = [unpack('<f', data[42:46])[0], unpack('<f', data[46: 50])[0], unpack('<f', data[50: 54])[0]]
	
	print(gyro)
	print(numpy.array(gyro).reshape(1, 3))
	print("------")
	

	#filt = Madgwick(numpy.array(gyro).reshape(1, 3), numpy.array(acc).reshape(1, 3), frequency=4)
	#print(filt)
	
	Q = numpy.tile([1., 0., 0., 0.], (1, 1))
	mag.updateIMU(Q, numpy.array(gyro), numpy.array(acc))
	print(Q)
	
	print(pyr[0], ", ", pyr[1], ", ", pyr[2])

	#print(data)

	#print(acc[0], ", ", acc[1], ", ", acc[2])

'''
from vpython import *
from time import *
import numpy as np
import math

scene.range=5
toRad=2*np.pi/360
toDeg=1/toRad
scene.forward=vector(-1,-1,-1)

scene.width=600
scene.height=600

xarrow=arrow(lenght=2, shaftwidth=.1, color=color.red,axis=vector(1,0,0))
yarrow=arrow(lenght=2, shaftwidth=.1, color=color.green,axis=vector(0,1,0))
zarrow=arrow(lenght=4, shaftwidth=.1, color=color.blue,axis=vector(0,0,1))

frontArrow=arrow(length=4,shaftwidth=.1,color=color.purple,axis=vector(1,0,0))
upArrow=arrow(length=1,shaftwidth=.1,color=color.magenta,axis=vector(0,1,0))
sideArrow=arrow(length=2,shaftwidth=.1,color=color.orange,axis=vector(0,0,1))

bBoard=box(length=6,width=2,height=.2,opacity=.8,pos=vector(0,0,0,))
bn=box(length=1,width=.75,height=.1, pos=vector(-.5,.1+.05,0),color=color.blue)
nano=box(lenght=1.75,width=.6,height=.1,pos=vector(-2,.1+.05,0),color=color.green)
acct = label(text="test\n", align='center', yoffset=250, color=color.green)

myObj=compound([bBoard,bn,nano])
count = 0


#ref = (0.9111927151679993 , 0.9111927151679993 , 0.01669277809560299 , 0.04780657961964607)

def q_mult(q1, q2):
	w1, x1, y1, z1 = q1
	w2, x2, y2, z2 = q2
	w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2

	x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
	y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
	z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
	return w, x, y, z

def q_conjugate(q):
	w, x, y, z = q
	return (w, -x, -y, -z)

def qv_mult(q1, v1):
	q2 = (0.0,) + v1
	return q_mult(q_mult(q1, q2), q_conjugate(q1))[1:]

def normalize(v, tolerance=0.00001):
	mag2 = sum(n * n for n in v)
	if abs(mag2 - 1.0) > tolerance:
		mag = sqrt(mag2)
		v = tuple(n / mag for n in v)
	return v

while (True):
	data, addr = sock.recvfrom(1024)

	acc = [unpack('<f', data[2:6])[0], unpack('<f', data[6: 10])[0], unpack('<f', data[10: 14])[0]]
	gyro = [unpack('<f', data[14:18])[0], unpack('<f', data[18: 22])[0], unpack('<f', data[22: 26])[0]]
	quat = [unpack('<f', data[26:30])[0], unpack('<f', data[30: 34])[0], unpack('<f', data[34: 38])[0], unpack('<f', data[38: 42])[0]]
	pyr = [unpack('<f', data[42:46])[0], unpack('<f', data[46: 50])[0], unpack('<f', data[50: 54])[0]]
	
	roll=float(pyr[2])*toRad
	pitch=float(pyr[0])*toRad
	yaw=float(pyr[1])*toRad+np.pi

	quaternion = (quat[0], quat[1], quat[2], quat[3])
	quaternion = normalize(quaternion)
	acc_vec = (acc[0], acc[1], acc[2])
	out = qv_mult(quaternion, acc_vec)
	print(pyr[0], ",", pyr[1], ",", pyr[2])
	#print("Roll=",roll*toDeg," Pitch=",pitch*toDeg,"Yaw=",yaw*toDeg)
	#print(count, ", ", acc[0], ", ", acc[1], ", ", acc[2])
	count += 1
	#print("Gyro X=", gyro[0], " gyro Y=", gyro[1], " gryo z=", gyro[2])
	rate(50)

	k=vector(cos(yaw)*cos(pitch), sin(pitch),sin(yaw)*cos(pitch))
	y=vector(0,1,0)
	s=cross(k,y)
	v=cross(s,k)
	print("K:",k)
	print("vROT: ", v)
	vrot=v*cos(roll)+cross(k,v)*sin(roll)

	frontArrow.axis=k
	sideArrow.axis=cross(k,vrot)
	upArrow.axis=vrot
	myObj.axis=k
	myObj.up=vrot
	sideArrow.length=2
	frontArrow.length=4
	upArrow.length=1
	acct.text = "Acc X: " + str(acc[0]) + ", Acc Y: " + str(acc[1]) + ", Acc Z: " + str(acc[2]) 