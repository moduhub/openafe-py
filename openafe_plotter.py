import matplotlib.pyplot as plt
from collections import deque
import serial


# MAX NO. OF POINTS TO STORE
queVoltage = deque(maxlen = 2000)
queCurrent = deque(maxlen = 2000)

ser = serial.Serial('COM6', 115200)


while True:
	# print(ser.readline())
	cc=str(ser.readline())
	# messageReceived = cc[2:][:-5] 
	messageReceived = cc[3:][:-8] 
	print(messageReceived)

	if messageReceived == "MSG,RDY":
		print('devide is ready!')
		
		# ser.write(b"$CVW,500,-500,250,10,2*47")
		ser.write(b"$CVW,500,-500,250,2,1*77")

		cc=str(ser.readline())
		messageReceived = cc[3:][:-8] 
		point = messageReceived[4:] 
		print(messageReceived)

		while messageReceived != "MSG,END":
			cc=str(ser.readline())
			messageReceived = cc[3:][:-8] 
			point = messageReceived[4:] 
			print(messageReceived)
			
			if messageReceived == "MSG,END":
				break

			pointObjs = point.split(',')

			voltage = float(pointObjs[0])
			current = float(pointObjs[1])

			queVoltage.append(voltage)
			queCurrent.append(current)
	
			# PLOTTING THE POINTS
			plt.plot(queVoltage, queCurrent)
			# plt.scatter(range(len(queVoltage)),queVoltage)

			# SET Y AXIS RANGE
			plt.xlim(-600,600)

			# DRAW, PAUSE AND CLEAR
			plt.draw()
			plt.pause(0.1)
			plt.clf()
		break

print("finished! UHUL!!!!") 