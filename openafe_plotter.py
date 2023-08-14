import matplotlib.pyplot as plt
from collections import deque
import serial


def getMessageFromOpenAFE():
	messageReceived=str(ser.readline())
	rawMessage = messageReceived[2:][:-5]
	print(rawMessage)
	# check the message's checksum ...
	isMessageOk = True
	if isMessageOk:
		message = messageReceived[3:][:-8] 
		return message
	else :
		return -1


def plotPoints(queVoltage, queCurrent):
	# PLOTTING THE POINTS
	plt.clf()
	plt.plot(queVoltage, queCurrent)

	# SET Y AXIS RANGE
	plt.xlim(-600,600)

	# DRAW, PAUSE AND CLEAR
	plt.draw()
	plt.pause(0.1)


fig, ax = plt.subplots()
line, = ax.plot([], [], 'o-')  # Create an empty line with markers ('o-')

# MAX NO. OF POINTS TO STORE
queVoltage = deque(maxlen = 2000)
queCurrent = deque(maxlen = 2000)

# Set the x and y data for the line
line.set_data(queVoltage, queCurrent)

ser = serial.Serial('COM6', 115200)

# Show the plot
plt.show(block=False)
plt.xlim(-600,600)

while True:
	messageReceived = getMessageFromOpenAFE()
	print(messageReceived)

	if messageReceived == -1:
		print("*** ERROR: Message corrupted!")
		break

	elif messageReceived == "MSG,RDY":
		print('devide is ready!')
		
		# ser.write(b"$CVW,500,-500,250,10,2*47")
		ser.write(b"$CVW,500,-500,250,2,1*77")

		messageReceived = getMessageFromOpenAFE() 

		while messageReceived != "MSG,END":
			messageReceived = getMessageFromOpenAFE()
			point = messageReceived[4:] 
			print(messageReceived)
			
			if messageReceived == "MSG,END":
				plotPoints(queVoltage, queCurrent)
				plt.pause(60)
				break

			pointObjs = point.split(',')

			voltage = float(pointObjs[0])
			current = float(pointObjs[1])

			queVoltage.append(voltage)
			queCurrent.append(current)

			if len(queVoltage) % 10 == 0: 
				plotPoints(queVoltage, queCurrent)

		break

print("finished! UHUL!!!!") 