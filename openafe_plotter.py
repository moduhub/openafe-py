import matplotlib.pyplot as plt
from collections import deque
import serial


def getMessageFromOpenAFE():
	"""
	The function `getMessageFromOpenAFE` reads a message from a serial port, checks its checksum, and
	returns the message if the checksum is valid, otherwise it returns -1.
	:return: either the message received from OpenAFE if the checksum is valid, or -1 if the checksum is
	not valid.
	"""
	messageReceived=str(ser.readline())
	rawMessage = messageReceived[2:][:-5]
	
	# check the message's checksum ...
	calculatedChecksum = calculateChecksumOfString(messageReceived[3:][:-8])
	checksumInMessage = getChecksumIntegerFromString(rawMessage[-2:])

	if (calculatedChecksum - checksumInMessage) == 0:
		# checksum is valid
		message = messageReceived[3:][:-8] 
		return message
	else :
		# checksum is not valid
		return -1


def calculateChecksumOfString(string):
	"""
	The function `calculateChecksumOfString` calculates the checksum of a given string by performing a
	bitwise XOR operation on the ASCII values of its characters.
	
	:param string: The parameter "string" is a string of characters for which we want to calculate the
	checksum, e.g.: "CVW,500,-500,250,2,1".
	:return: the checksum of the given string, e.g.: 119 (0x77).
	"""
	checksum = 0
	for char in string:
		checksum = (checksum ^ ord(char))
	return checksum


def getChecksumIntegerFromString(checksumString):
	"""
	The function `getChecksumIntegerFromString` converts a string representation of a checksum into an
	integer value.
	
	:param checksumString: The `checksumString` parameter is a string that represents a checksum, e.g.: "32".
	:return: an integer checksum value e.g.: 50 (0x32).
	"""
	integerChecksum = 0
	index = 1

	for char in checksumString:
		if ord(char) < 0x41:
			integerChecksum |= (ord(char) - 0x30) << (index * 4)
		else:
			integerChecksum |= (ord(char) - 0x37) << (index * 4)
		index -= 1

	return integerChecksum


def sendCommandToMCU(command):
	"""
	The function `sendCommandToMCU` sends a command to a microcontroller unit (MCU) by calculating a
	checksum, constructing a full command string, and writing it to a serial port.
	
	:param command: The `command` parameter is a string that represents the command to be sent to the
	MCU (Microcontroller Unit), e.g.: "CVW,500,-500,250,2,1".
	"""
	checksumString = hex(calculateChecksumOfString(command))
	checksumString = checksumString[2:] # removes the "0x"
	fullCommand = "$" + command + "*" + checksumString
	print("full command sent: ", fullCommand)
	ser.write(fullCommand.encode("utf-8"))


def plotPoints(queVoltage, queCurrent):
	"""
	The function "plotPoints" plots points on a graph and sets the y-axis range.
	
	:param queVoltage: The queVoltage parameter represents the list of voltage values that you want to
	plot on the x-axis. Each value in the list corresponds to a point on the plot
	:param queCurrent: The queCurrent parameter represents the list of current values that you want to
	plot on the y-axis. Each value in the list corresponds to a specific point on the plot
	"""
	# PLOTTING THE POINTS
	plt.clf()
	plt.plot(queVoltage, queCurrent)

	# SET Y AXIS RANGE
	plt.xlim(-600,600)

	# DRAW, PAUSE AND CLEAR
	plt.draw()
	plt.pause(0.1)


# ***** ***** ***** MAIN ***** ***** *****:

# MAX NO. OF POINTS TO STORE
queVoltage = deque(maxlen = 2000)
queCurrent = deque(maxlen = 2000)

ser = serial.Serial('COM6', 115200)

# Show the plot
plt.show(block=False)
plt.xlim(-600,600)

while True:
	messageReceived = getMessageFromOpenAFE()

	if messageReceived == -1:
		print("*** ERROR: Message corrupted!")
		break

	elif messageReceived == "MSG,RDY":
		# ser.write(b"$CVW,500,-500,250,10,2*47")
		# ser.write(b"$CVW,500,-500,250,2,1*77")
		sendCommandToMCU("CVW,500,-500,250,2,1")

		messageReceived = getMessageFromOpenAFE() 

		while messageReceived != "MSG,END":
			messageReceived = getMessageFromOpenAFE()
			point = messageReceived[4:] 
			print(messageReceived[4:])
			
			if messageReceived == "MSG,END":
				plotPoints(queVoltage, queCurrent)
				plt.pause(60)
				break

			elif messageReceived != -1: # if message is valid
				pointObjs = point.split(',')

				voltage = float(pointObjs[0])
				current = float(pointObjs[1])

				queVoltage.append(voltage)
				queCurrent.append(current)

				if len(queVoltage) % 20 == 0: 
					plotPoints(queVoltage, queCurrent)
			
		break

print("finished! UHUL!!!!") 