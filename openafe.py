import serial
import sys

class OpenAFE:

	def __init__(self, comPort, onPointCallback=None, onEndCallback=None):
		"""
		The above code defines a Python class with an initialization method that establishes a serial
		connection and sets optional callback functions.
		
		:param comPort: The comPort parameter is the serial port to which the OpenAFE device is connected.
		It is used to establish a connection with the device
		:param onPointCallback: The onPointCallback parameter is a function that will be called whenever a
		data point is received from the OpenAFE device. This function can be used to process or display the
		received data point
		:param onEndCallback: The `onEndCallback` parameter is a callback function that will be called when
		the communication with the OpenAFE device ends. It is an optional parameter, so if you don't provide
		a callback function, it will default to `None`
		"""
		try:
			self.ser = serial.Serial(comPort, 115200)
		except serial.serialutil.SerialException as e:
			print("*** ERROR: failed to stablish connection with the OpenAFE device. CHECK IF IT IS CONNECTED")
			sys.exit(1)

		self.onPointCallback = onPointCallback
		self.onEndCallback = onEndCallback


	def waitForMessage(self):
		"""
		The `waitForMessage` function reads a message from a serial port, checks its checksum, and returns
		the message if the checksum is valid, otherwise it returns -1.
		:return: The function `waitForMessage` returns either the message received from OpenAFE if the
		checksum is valid, or -1 if the checksum is not valid.
		"""
		try:
			messageReceived=str(self.ser.readline())
		except serial.serialutil.SerialException as e:
			print("*** ERROR: failed to read from the OpenAFE device. CHECK IF IT IS CONNECTED")
			sys.exit(1)

		rawMessage = messageReceived[2:][:-5]
		
		# check the message's checksum ...
		calculatedChecksum = self._calculateChecksumOfString(messageReceived[3:][:-8])
		checksumInMessage = self._getChecksumIntegerFromString(rawMessage[-2:])

		if (calculatedChecksum - checksumInMessage) == 0:
			# checksum is valid
			message = messageReceived[3:][:-8] 
			return message
		else :
			# checksum is not valid
			return -1


	def isValidMessage(self, message):
		"""
		NOTE: This functions does not check if the message is an error message, it checks if the message 
		received is valid, in other words, if it was not corrupted during its transmission.

		The function `isValidMessage` checks if a given message is valid by comparing it to -1.
		
		:param message: The parameter "message" is a variable that represents the message being checked for
		validity
		:return: True if the message is equal to -1, and False otherwise.
		"""
		if message == -1:
			return True
		else:
			return False


	def isErrorMessage(self, message):
		"""
		NOTE: This function only checks if the message is an error message, but not if the message received
		is valid. Invalid messages have a value of -1. 

		The function checks if a given message is an error message by checking if it begins with "ERR".
		
		:param message: The parameter "message" is a string that represents a message
		:return: a boolean value. If the message begins with "ERR", it will return True. Otherwise, it will
		return False.
		"""
		if message[:-4] == "ERR":
			return True
		else:
			return False


	def _calculateChecksumOfString(self, string):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The function `_calculateChecksumOfString` calculates the checksum of a given string by performing a
		bitwise XOR operation on the ASCII values of its characters.
		
		:param string: The parameter "string" is a string of characters for which we want to calculate the
		checksum, e.g.: "CVW,500,-500,250,2,1".
		:return: the checksum of the given string, e.g.: 119 (0x77).
		"""
		checksum = 0
		for char in string:
			checksum = (checksum ^ ord(char))
		return checksum


	def _getChecksumIntegerFromString(self, checksumString):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The function `_getChecksumIntegerFromString` converts a string representation of a checksum into an
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


	def sendCommandToMCU(self, command):
		"""
		The `sendCommandToMCU` function sends a command to a microcontroller unit (MCU) by calculating a
		checksum, constructing a full command string, and writing it to a serial port.
		
		:param command: The `command` parameter is a string that represents the command to be sent to the
		MCU (Microcontroller Unit). It can be any valid command that the MCU understands. For example,
		"CVW,500,-500,250,2,1" is a command that instructs the MCU to
		"""
		try:
			checksum = self._calculateChecksumOfString(command)
			checksumString = format(checksum, '02X')
			fullCommand = "$" + command + "*" + checksumString
			# print("full command: ", fullCommand)
			self.ser.write(fullCommand.encode("utf-8"))

		except serial.serialutil.SerialException as e:
			print("*** ERROR: failed to send command to the OpenAFE device. CHECK IF IT IS CONNECTED")
			sys.exit(1)


	def setCurrentRange(self, currentRange):
		"""
		The function sets the current range of an OpenAFE device and returns True if successful, or False if
		there was an error.
		
		:param currentRange: The currentRange parameter is the desired range of current that the OpenAFE
		device should use. It is a numerical value that represents the range in amperes
		:return: a boolean value. If the current range was set successfully, it returns True. If there was
		an error and the current range was not set, it returns False.
		"""
		self.sendCommandToMCU("CMD,CUR," + str(currentRange))
		if self.isErrorMessage(self.waitForMessage()):
			print("*** ERROR: Current range was not set. OBS: OpenAFE device will be using the default current range.")
			return False
		else:
			return True


	def makeCyclicVoltammetry(self, endingPotential, startingPotential, scanRate, stepSize, numberOfCycles, settlingTime):
		"""
		The function "makeCyclicVoltammetry" sends a command string to a microcontroller unit (MCU) to
		perform cyclic voltammetry with specified parameters.
		
		:param endingPotential: The ending potential is the final voltage value at which the cyclic
		voltammetry will stop. It is a floating-point number representing the voltage in volts, in millivolts (mV)
		:param startingPotential: The starting potential is the initial voltage at which the cyclic
		voltammetry experiment begins, in millivolts (mV)
		:param scanRate: The scan rate is the rate at which the potential is swept during the cyclic
		voltammetry experiment. It is usually expressed in millivolts per second (mV/s)
		:param stepSize: The step size is the increment or decrement in potential applied during each step
		of the cyclic voltammetry experiment. It determines the resolution of the measurement and can be
		positive or negative, in millivolts (mV)
		:param numberOfCycles: The numberOfCycles parameter specifies the number of cycles to perform in the
		cyclic voltammetry experiment
		:param settlingTime: The settlingTime parameter refers to the time in seconds that the system should
		wait before starting the cyclic voltammetry measurement. This allows the system to stabilize and
		reach a steady state before the measurement begins, in milliseconds (ms)
		"""
		CVCommandString = "CVW," + str(endingPotential) + "," + str(startingPotential) + \
		"," + str(scanRate) + "," + str(stepSize) + "," + str(numberOfCycles)
		self.sendCommandToMCU(CVCommandString) # send the CV command


	def receiveVoltammetryPoints(self):
		"""
		The function `receiveVoltammetryPoints` receives messages from OpenAFE, processes the received
		points, and calls the appropriate callbacks.
		"""
		while True:
			messageReceived = self.waitForMessage()
			point = messageReceived[4:]

			if messageReceived == "MSG,END":
				self._onVoltammetryEnd()
				break
			
			if messageReceived[:-4] == "ERR":
				print("*** ERROR: An error ocurred")
				break

			elif messageReceived != -1: # if message is valid
				pointObjs = point.split(',')

				voltage = float(pointObjs[0])
				current = float(pointObjs[1])

				self._onVoltammetryPoint(voltage, current)


	def _onVoltammetryPoint(self, voltage, current):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The `_onVoltammetryPoint` function takes in a voltage and current value and calls a callback function
		if it exists.
		
		:param voltage: The voltage value at a specific point in a voltammetry experiment
		:param current: The current parameter represents the measured electric current in the voltammetry
		experiment
		"""
		if self.onPointCallback and callable(self.onPointCallback):
			self.onPointCallback(voltage, current)


	def _onVoltammetryEnd(self):
		"""
		NOTE: PRIVATE METHOD, DO NOT CALL IT!

		The function `_onVoltammetryEnd` checks if a callback function `onEndCallback` is defined and
		callable, and if so, it calls the callback function.
		"""
		if self.onEndCallback and callable(self.onEndCallback):
			self.onEndCallback()